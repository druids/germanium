import logging

from django.test.client import Client
from django.test.client import RequestFactory

from germanium import config
from germanium.tools import assert_http_redirect, capture_on_commit_callbacks

from .auth import AuthTestCaseMixin
from .default import GermaniumSimpleTestCase, GermaniumTestCase


class ClientTestCaseMixin(AuthTestCaseMixin):

    logger = logging.getLogger('tests')

    def setUp(self):
        self.c = Client()
        self.r_factory = RequestFactory()
        self.default_headers = {}
        super().setUp()

    def get_request_with_user(self, request):
        request.user = self.logged_user.user
        return request

    def logout(self):
        self.get(config.LOGOUT_URL)
        self.logged_user = None

    def authorize(self, username, password):
        assert_http_redirect(self.post(config.LOGIN_URL, {config.USERNAME: username, config.PASSWORD: password}))

    def get(self, url, headers=None, execute_on_commit=False, execute_on_commit_cascade=False):
        headers = headers or {}
        headers.update(self.default_headers)

        with capture_on_commit_callbacks(execute=execute_on_commit, execute_cascade=execute_on_commit_cascade):
            resp = self.c.get(url, **headers)
        return resp

    def put(self, url, data={}, headers=None, execute_on_commit=False, execute_on_commit_cascade=False):
        headers = headers or {}
        headers.update(self.default_headers)

        if execute_on_commit:
            with capture_on_commit_callbacks(execute=execute_on_commit, execute_cascade=execute_on_commit_cascade):
                resp = self.c.put(url, data, **self.headers)
        else:
            resp = self.c.put(url, data, **self.headers)
        return resp


    def post(self, url, data, headers=None, execute_on_commit=False, execute_on_commit_cascade=False):
        headers = headers or {}
        headers.update(self.default_headers)

        with capture_on_commit_callbacks(execute=execute_on_commit, execute_cascade=execute_on_commit_cascade):
            resp = self.c.post(url, data, **headers)
        return resp

    def head(self, url, headers=None, execute_on_commit=False, execute_on_commit_cascade=False):
        headers = headers or {}
        headers.update(self.default_headers)

        with capture_on_commit_callbacks(execute=execute_on_commit, execute_cascade=execute_on_commit_cascade):
            resp = self.c.head(url, **headers)
        return resp

    def options(self, url, headers=None, execute_on_commit=False, execute_on_commit_cascade=False):
        headers = headers or {}
        headers.update(self.default_headers)

        with capture_on_commit_callbacks(execute=execute_on_commit, execute_cascade=execute_on_commit_cascade):
            resp = self.c.options(url, **headers)
        return resp

    def delete(self, url, headers=None, execute_on_commit=False, execute_on_commit_cascade=False):
        headers = headers or {}
        headers.update(self.default_headers)

        with capture_on_commit_callbacks(execute=execute_on_commit, execute_cascade=execute_on_commit_cascade):
            resp = self.c.delete(url, **headers)
        return resp


class ClientTestCase(ClientTestCaseMixin, GermaniumTestCase):
    pass


class SimpleClientTestCase(ClientTestCaseMixin, GermaniumSimpleTestCase):
    pass
