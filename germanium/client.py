from __future__ import unicode_literals

import logging

from django.test.client import Client
from django.test.testcases import LiveServerTestCase
from django.test.client import RequestFactory

from germanium.auth import AuthTestCaseMixin
from germanium import config
from germanium.asserts import AssertMixin


class ClientTestCase(AuthTestCaseMixin, LiveServerTestCase, AssertMixin):

    logger = logging.getLogger('tests')

    def setUp(self):
        self.c = Client()
        self.r_factory = RequestFactory()
        self.default_headers = {}
        super(ClientTestCase, self).setUp()

    def get_request_with_user(self, request):
        request.user = self.logged_user.user
        return request

    def logout(self):
        self.get(config.LOGOUT_URL)
        self.logged_user = None

    def authorize(self, username, password):
        resp = self.post(config.LOGIN_URL, {config.USERNAME: username, config.PASSWORD: password})
        self.assert_http_redirect(resp)

    def get(self, url, headers=None):
        headers = headers or {}
        headers.update(self.default_headers)

        resp = self.c.get(url, **headers)
        return resp

    def put(self, url, data={}, headers=None):
        headers = headers or {}
        headers.update(self.default_headers)

        return self.c.put(url, data, **self.headers)

    def post(self, url, data, headers=None):
        headers = headers or {}
        headers.update(self.default_headers)

        return self.c.post(url, data, **headers)

    def head(self, url, headers=None):
        headers = headers or {}
        headers.update(self.default_headers)

        return self.c.head(url, **headers)

    def options(self, url, headers=None):
        headers = headers or {}
        headers.update(self.default_headers)

        return self.c.options(url, **headers)

    def delete(self, url, headers=None):
        headers = headers or {}
        headers.update(self.default_headers)

        resp = self.c.delete(url, **headers)
        return resp

    def assert_http_ok(self, resp, msg=None):
        return self.assert_equal(resp.status_code, 200, msg)

    def assert_http_created(self, resp, msg=None):
        return self.assert_equal(resp.status_code, 201, msg)

    def assert_http_accepted(self, resp, msg=None):
        return self.assert_in(resp.status_code, [202, 204], msg)

    def assert_http_multiple_choices(self, resp, msg=None):
        return self.assertEqual(resp.status_code, 300, msg)

    def assert_http_redirect(self, resp, msg=None):
        """
        Ensures the response is returning a HTTP 302.
        """
        return self.assertEqual(resp.status_code, 302, msg)

    def assert_http_see_other(self, resp, msg=None):
        """
        Ensures the response is returning a HTTP 303.
        """
        return self.assertEqual(resp.status_code, 303, msg)

    def assert_http_not_modified(self, resp, msg=None):
        """
        Ensures the response is returning a HTTP 304.
        """
        return self.assertEqual(resp.status_code, 304, msg)

    def assert_http_bad_request(self, resp, msg=None):
        """
        Ensures the response is returning a HTTP 400.
        """
        return self.assertEqual(resp.status_code, 400, msg)

    def assert_http_unauthorized(self, resp, msg=None):
        """
        Ensures the response is returning a HTTP 401.
        """
        return self.assertEqual(resp.status_code, 401, msg)

    def assert_http_forbidden(self, resp, msg=None):
        """
        Ensures the response is returning a HTTP 403.
        """
        return self.assertEqual(resp.status_code, 403, msg)

    def assert_http_not_found(self, resp, msg=None):
        """
        Ensures the response is returning a HTTP 404.
        """
        return self.assertEqual(resp.status_code, 404, msg)

    def assert_http_method_not_allowed(self, resp, msg=None):
        """
        Ensures the response is returning a HTTP 405.
        """
        return self.assertEqual(resp.status_code, 405, msg)

    def assert_http_conflict(self, resp, msg=None):
        """
        Ensures the response is returning a HTTP 409.
        """
        return self.assertEqual(resp.status_code, 409, msg)

    def assert_http_gone(self, resp, msg=None):
        """
        Ensures the response is returning a HTTP 410.
        """
        return self.assertEqual(resp.status_code, 410, msg)

    def assert_http_unprocessable_entity(self, resp, msg=None):
        """
        Ensures the response is returning a HTTP 422.
        """
        return self.assertEqual(resp.status_code, 422, msg)

    def assert_http_too_many_requests(self, resp, msg=None):
        """
        Ensures the response is returning a HTTP 429.
        """
        return self.assertEqual(resp.status_code, 429, msg)

    def assert_http_application_error(self, resp, msg=None):
        """
        Ensures the response is returning a HTTP 500.
        """
        return self.assertEqual(resp.status_code, 500, msg)

    def assert_http_not_implemented(self, resp, msg=None):
        """
        Ensures the response is returning a HTTP 501.
        """
        return self.assertEqual(resp.status_code, 501, msg)
