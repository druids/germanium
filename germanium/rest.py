from __future__ import unicode_literals

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_text
from django.test.client import MULTIPART_CONTENT

from germanium.client import ClientTestCase
from germanium import config
from germanium.asserts import AssertMixin


class RESTTestCase(ClientTestCase, AssertMixin):

    def setUp(self):
        super(RESTTestCase, self).setUp()

    def authorize(self, username, password):
        self.assert_http_redirect(self.post(config.LOGIN_URL, {config.USERNAME: username,
                                                               config.PASSWORD: password},
                                            content_type=MULTIPART_CONTENT))

    def put(self, url, data={}, content_type='application/json', headers=None):
        headers = headers or {}
        headers.update(self.default_headers)

        return self.c.put(url, data=data, content_type=content_type, **headers)

    def post(self, url, data, content_type='application/json', headers=None):
        headers = headers or {}
        headers.update(self.default_headers)

        return self.c.post(url, data=data, content_type=content_type, **headers)

    def assert_valid_JSON(self, data, msg='Json is not valid'):
        """
        Given the provided ``data`` as a string, ensures that it is valid JSON &
        can be loaded properly.
        """
        try:
            json.loads(data)
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
        self.assert_valid_JSON(force_text(resp.content), msg)

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
        self.assert_valid_JSON(force_text(resp.content), msg)

    def deserialize(self, resp):
        """
        Given a ``HttpResponse`` coming back from using the ``client``, this method
        return dict of deserialized json string
        """
        return json.loads(resp.content.decode('utf-8'))

    def serialize(self, data):
        """
        Given a Python datastructure (typically a ``dict``) & a desired  json,
        this method will return a serialized string of that data.
        """
        return json.dumps(data, cls=DjangoJSONEncoder)

    def assert_keys(self, data, expected):
        """
        This method ensures that the keys of the ``data`` match up to the keys of
        ``expected``.

        It covers the (extremely) common case where you want to make sure the keys of
        a response match up to what is expected. This is typically less fragile than
        testing the full structure, which can be prone to data changes.
        """
        self.assert_equal(sorted(data.keys()), sorted(expected))
