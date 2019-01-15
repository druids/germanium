import logging

from django.test.client import Client
from django.test.client import RequestFactory

from germanium import config
from germanium.tools.http import assert_http_redirect

from .auth import AuthTestCaseMixin
from .default import GermaniumSimpleTestCase, GermaniumTestCase


class ClientTestCaseMixin(AuthTestCaseMixin):

    logger = logging.getLogger('tests')

    def setUp(self):
        self.c = Client()
        self.r_factory = RequestFactory()
        self.default_headers = {}
        super(ClientTestCaseMixin, self).setUp()

    def get_request_with_user(self, request):
        request.user = self.logged_user.user
        return request

    def logout(self):
        self.get(config.LOGOUT_URL)
        self.logged_user = None

    def authorize(self, username, password):
        assert_http_redirect(self.post(config.LOGIN_URL, {config.USERNAME: username, config.PASSWORD: password}))

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


class ClientTestCase(ClientTestCaseMixin, GermaniumTestCase):
    pass


class SimpleClientTestCase(ClientTestCaseMixin, GermaniumSimpleTestCase):
    pass
