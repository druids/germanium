import json

from django.core.serializers.json import DjangoJSONEncoder
from django.test.client import MULTIPART_CONTENT

from germanium import config
from germanium.tools import assert_http_redirect, capture_on_commit_callbacks

from .client import ClientTestCaseMixin
from .default import GermaniumTestCase, GermaniumSimpleTestCase


JSON_CONTENT_TYPE = 'application/json'


class RESTTestCaseMixin(ClientTestCaseMixin):

    SERIALIZERS = {
        JSON_CONTENT_TYPE: lambda data: json.dumps(data, cls=DjangoJSONEncoder),
        MULTIPART_CONTENT: lambda data: data,
    }

    DESERIALIZERS = {
        JSON_CONTENT_TYPE: lambda resp: json.loads(resp.content.decode('utf-8')),
        MULTIPART_CONTENT: lambda resp: resp,
    }

    def authorize(self, username, password):
        assert_http_redirect(self.post(config.LOGIN_URL, {config.USERNAME: username,
                                                          config.PASSWORD: password},
                                            content_type=MULTIPART_CONTENT))

    def get(self, url, content_type=None, headers=None, execute_on_commit=False,
            execute_on_commit_cascade=False):
        content_type = content_type or JSON_CONTENT_TYPE
        headers = headers or {}
        headers['Accept'] = headers.get('Accept', content_type)
        headers.update(self.default_headers)

        with capture_on_commit_callbacks(execute=execute_on_commit, execute_cascade=execute_on_commit_cascade):
            resp = self.c.get(url, content_type=content_type, **headers)
        return resp

    def put(self, url, data={}, content_type=None, headers=None, execute_on_commit=False,
            execute_on_commit_cascade=False):
        content_type = content_type or JSON_CONTENT_TYPE
        headers = headers or {}
        headers['Accept'] = headers.get('Accept', content_type)
        headers.update(self.default_headers)

        with capture_on_commit_callbacks(execute=execute_on_commit, execute_cascade=execute_on_commit_cascade):
            resp = self.c.put(url, data=self.serialize(data, content_type) if data is not None else data,
                              content_type=content_type, **headers)
        return resp

    def post(self, url, data, content_type=None, headers=None, execute_on_commit=False,
             execute_on_commit_cascade=False):
        content_type = content_type or JSON_CONTENT_TYPE
        headers = headers or {}
        headers['Accept'] = headers.get('Accept', content_type)
        headers.update(self.default_headers)

        with capture_on_commit_callbacks(execute=execute_on_commit, execute_cascade=execute_on_commit_cascade):
            resp = self.c.post(url, data=self.serialize(data, content_type) if data is not None else data,
                               content_type=content_type, **headers)
        return resp

    def patch(self, url, data, content_type=None, headers=None, execute_on_commit=False,
              execute_on_commit_cascade=False):
        content_type = content_type or JSON_CONTENT_TYPE
        headers = headers or {}
        headers['Accept'] = headers.get('Accept', content_type)
        headers.update(self.default_headers)

        with capture_on_commit_callbacks(execute=execute_on_commit, execute_cascade=execute_on_commit_cascade):
            resp = self.c.patch(url, data=self.serialize(data, content_type) if data is not None else data,
                                content_type=content_type, **headers)
        return resp

    def delete(self, url, content_type=None, headers=None, execute_on_commit=False,
               execute_on_commit_cascade=False):
        content_type = content_type or JSON_CONTENT_TYPE
        headers = headers or {}
        headers['Accept'] = headers.get('Accept', content_type)
        headers.update(self.default_headers)

        with capture_on_commit_callbacks(execute=execute_on_commit, execute_cascade=execute_on_commit_cascade):
            resp = self.c.delete(url, **headers)
        return resp

    def deserialize(self, resp, content_type=None):
        """
        Given a ``HttpResponse`` coming back from using the ``client``, this method
        return dict of deserialized json string
        """
        content_type = content_type or JSON_CONTENT_TYPE
        deserializer = self.DESERIALIZERS.get(content_type)
        if deserializer is None:
            raise NotImplementedError('Missing DEserializer')
        else:
            return deserializer(resp)

    def serialize(self, data, content_type=None):
        """
        Given a Python datastructure (typically a ``dict``) & a desired  json,
        this method will return a serialized string of that data.
        """
        content_type = content_type or JSON_CONTENT_TYPE
        serializer = self.SERIALIZERS.get(content_type)
        if serializer is None:
            raise NotImplementedError('Missing serializer')
        else:
            return serializer(data)


class RESTTestCase(RESTTestCaseMixin, GermaniumTestCase):
    pass


class SimpleRESTTestCase(RESTTestCaseMixin, GermaniumSimpleTestCase):
    pass
