from __future__ import unicode_literals

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_text
from django.test.client import MULTIPART_CONTENT

from germanium.client import ClientTestCase
from germanium import config
from germanium.asserts import AssertMixin


JSON_CONTENT_TYPE = 'application/json'


class RESTTestCase(ClientTestCase, AssertMixin):

    SERIALIZERS = {
        JSON_CONTENT_TYPE: lambda data: json.dumps(data, cls=DjangoJSONEncoder),
        MULTIPART_CONTENT: lambda data: data,
    }

    DESERIALIZERS = {
        JSON_CONTENT_TYPE: lambda resp: json.loads(resp.content.decode('utf-8')),
        MULTIPART_CONTENT: lambda resp: resp,
    }

    def setUp(self):
        super(RESTTestCase, self).setUp()

    def authorize(self, username, password):
        self.assert_http_redirect(self.post(config.LOGIN_URL, {config.USERNAME: username,
                                                               config.PASSWORD: password},
                                            content_type=MULTIPART_CONTENT))

    def get(self, url, content_type=None, headers=None):
        content_type = content_type or JSON_CONTENT_TYPE
        headers = headers or {}
        headers['Accept'] = headers.get('Accept', content_type)
        headers.update(self.default_headers)

        resp = self.c.get(url, content_type=content_type, **headers)
        return resp

    def put(self, url, data={}, content_type=None, headers=None):
        content_type = content_type or JSON_CONTENT_TYPE
        headers = headers or {}
        headers['Accept'] = headers.get('Accept', content_type)
        headers.update(self.default_headers)

        return self.c.put(url, data=self.serialize(data, content_type) if data is not None else data,
                          content_type=content_type, **headers)

    def post(self, url, data, content_type=None, headers=None):
        content_type = content_type or JSON_CONTENT_TYPE
        headers = headers or {}
        headers['Accept'] = headers.get('Accept', content_type)
        headers.update(self.default_headers)

        return self.c.post(url, data=self.serialize(data, content_type) if data is not None else data,
                           content_type=content_type, **headers)

    def delete(self, url, content_type=None, headers=None):
        content_type = content_type or JSON_CONTENT_TYPE
        headers = headers or {}
        headers['Accept'] = headers.get('Accept', content_type)
        headers.update(self.default_headers)

        resp = self.c.delete(url, **headers)
        return resp

    def assert_valid_JSON(self, data, msg='Json is not valid'):
        """
        Given the provided ``data`` as a string, ensures that it is valid JSON &
        can be loaded properly.
        """
        try:
            json.loads(force_text(data))
        except:
            self.fail(msg)

    def assert_valid_JSON_response(self, resp, msg=None):
        """
        Given a ``HttpResponse`` coming back from using the ``client``, assert that
        you get back:

        * An HTTP 200
        * The correct content-type (``application/json``)
        * The content is valid JSON
        """
        self.assert_http_ok(resp, msg)
        self.assert_true(resp['Content-Type'].startswith('application/json'), msg)
        self.assert_valid_JSON(resp.content, msg)

    def assert_valid_JSON_created_response(self, resp, msg=None):
        """
        Given a ``HttpResponse`` coming back from using the ``client``, assert that
        you get back:

        * An HTTP 201
        * The correct content-type (``application/json``)
        * The content is valid JSON
        """
        self.assert_http_created(resp, msg)
        self.assert_true(resp['Content-Type'].startswith('application/json'), msg)
        self.assert_valid_JSON(resp.content, msg)

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

    def assert_keys(self, data, expected):
        """
        This method ensures that the keys of the ``data`` match up to the keys of
        ``expected``.

        It covers the (extremely) common case where you want to make sure the keys of
        a response match up to what is expected. This is typically less fragile than
        testing the full structure, which can be prone to data changes.
        """
        self.assert_equal(sorted(data.keys()), sorted(expected))
