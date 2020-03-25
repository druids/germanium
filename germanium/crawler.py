import re

import logging

from urllib.parse import urlparse, urljoin
from html.parser import HTMLParser

from django.conf import settings


LOG = logging.getLogger('tests')


class LinkExtractor:

    def extract(self, content):
        raise NotImplementedError


class DummyLinkExtractor(LinkExtractor):

    def extract(self, content):
        return []


class HTMLLinkExtractor(LinkExtractor):

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


class URLWithReferer:

    def __init__(self, url, referer=None):
        self.url = url
        self.referer = referer

    def __eq__(self, other):
        if isinstance(other, URLWithReferer):
            return self.url == other.url
        if isinstance(object, str):
            return self.url == other
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.url

    def __hash__(self):
        return hash(self.url)

    def __unicode__(self):
        return self.url


class Crawler:

    def __init__(self, client, base_urls=None, exclude_urls=None, pre_request=None, post_response=None,
                 extra_link_extractors=None):
        self.client = client
        self.urls = set()
        if base_urls:
            for url in base_urls:
                self.urls.add(URLWithReferer(url))

        self.crawled_urls = set()
        self.exclude_urls = set(exclude_urls or ())
        self.pre_request = pre_request
        self.post_response = post_response
        self.link_extractors = {
            'text/html': HTMLLinkExtractor(),
            'default': DummyLinkExtractor(),
        }
        if extra_link_extractors:
            self.link_extractors.update(extra_link_extractors)
        self.excluded_urls_regexs = [re.compile(r'^{}$'.format(url)) for url in self.exclude_urls]

    def run(self):
        while self.urls:
            self._call_request(self.urls.pop())

    def _parse_urls(self, url, resp):
        returned_urls = []
        content_type = resp['Content-Type'].split(';')[0]
        if content_type in self.link_extractors:
            content = resp.content
            if 'utf-8' in resp['Content-Type']:
                content = content.decode('utf-8')

            for link in self.link_extractors.get(content_type, self.link_extractors['default']).extract(content):
                parsed_href = urlparse(link)

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
                    returned_urls.append(urljoin(url, link))

        return returned_urls

    def _pre_request(self, url, referer, headers):
        if self.pre_request:
            self.pre_request(url, referer, headers)

        return url, headers

    def _post_response(self, url, referer, resp=None, exception=None):
        if self.post_response:
            self.post_response(url, referer, resp, exception)

    def _call_request(self, url_with_referer):
        url, referer = url_with_referer.url, url_with_referer.referer
        resp = None
        try:
            url, headers = self._pre_request(url, referer, {})
            resp = self.client.get(url, follow=True, **headers)
            self.crawled_urls.add(url)
            if resp.redirect_chain:
                self.crawled_urls.update((redirect_url for redirect_url, _ in resp.redirect_chain))
            for parsed_url in self._parse_urls(url, resp):
                if (parsed_url not in self.crawled_urls and parsed_url not in self.urls and
                        not any(excluded_urls_regex.match(parsed_url)
                                for excluded_urls_regex in self.excluded_urls_regexs)):
                    self.urls.add(URLWithReferer(parsed_url, url))
            self._post_response(url, referer, resp)
        except Exception as e:
            LOG.exception('%s had unhandled exception: %s', url, e)
            self._post_response(url, referer, resp, e)
