import logging
import urlparse

from HTMLParser import HTMLParseError, HTMLParser
from django.conf import settings


LOG = logging.getLogger('tests')


class LinkExtractor():

    def extract(self, content):
        raise NotImplementedError


class HtmlLinkExtractor(LinkExtractor):

    link_attr_names = ('href', 'src')


    def extract(self, content):
        link_attr_names = self.link_attr_names

        class SaxLinkExtractor(HTMLParser):
            links = set()

            def handle_starttag(self, tag, attrs):
                self.links.update(
                    v for k, v in attrs if k in link_attr_names
            )

        parser = SaxLinkExtractor()
        parser.feed(content)
        parser.close()

        return parser.links


class Crawler(object):

    def __init__(self, client, base_urls=None, exclude_urls=None, pre_request=None, post_response=None, extra_link_extractors=None):
        self.client = client
        self.urls = set(base_urls or ())
        self.crawled_urls = set(exclude_urls or ())
        self.pre_request = pre_request
        self.post_response = post_response
        self.link_extractors = {'default': HtmlLinkExtractor()}
        if extra_link_extractors:
            self.link_extractors.update(extra_link_extractors)

    def run(self):
        while self.urls:
            url = self.urls.pop()
            self._call_request(url)

    def _parse_urls(self, url, resp):
        content = resp.content
        if 'utf-8' in resp['Content-Type']:
            content = content.decode('utf-8')

        returned_urls = []

        for link in self.link_extractors.get(resp['Content-Type'], self.link_extractors['default']).extract(content):
            parsed_href = urlparse.urlparse(link)

            if not parsed_href.path:
                continue

            if parsed_href.scheme and not parsed_href.netloc.startswith('testserver'):
                LOG.debug('Skipping external link: %s', link)
                continue

            if ('django.contrib.staticfiles' in settings.INSTALLED_APPS
                and parsed_href.path.startswith(settings.STATIC_URL)):
                LOG.debug('Skipping static file %s', parsed_href.path)
            elif parsed_href.path.startswith(settings.MEDIA_URL):
                LOG.debug('Skipping media file %s', parsed_href.path)
            elif parsed_href.path.startswith('/'):
                returned_urls.append(link)
            else:
                # We'll use urlparse's urljoin since that handles things like <a href="../foo">
                returned_urls.append(urlparse.urljoin(url, link))

        return returned_urls

    def _pre_request(self, url, headers):
        if self.pre_request:
            self.pre_request(url, headers)

        return url, headers

    def _post_response(self, url, resp, exception=None):
        if self.post_response:
            self.post_response(url, resp, exception)

    def _call_request(self, url):
        try:
            url, headers = self._pre_request(url, {})
            resp = self.client.get(url, follow=True, **headers)
            self.crawled_urls.add(url)
            if resp.redirect_chain:
                self.crawled_urls.update((redirect_url for redirect_url, _ in resp.redirect_chain))
            for parsed_url in self._parse_urls(url, resp):
                if parsed_url not in self.crawled_urls and parsed_url not in self.urls:
                    self.urls.add(parsed_url)
            e = None
        except HTMLParseError, e:
            LOG.error('%s: unable to parse invalid HTML: %s', url, e)
        except Exception, e:
            LOG.exception('%s had unhandled exception: %s', url, e)

        self._post_response(url, resp, e)
