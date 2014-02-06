from django.test.client import Client
from django.test.testcases import LiveServerTestCase

from germanium.auth import AuthTestCaseMixin
from germanium import config


class ClientTestCase(AuthTestCaseMixin, LiveServerTestCase):

    def setUp(self):
        self.c = Client()
        super(ClientTestCase, self).setUp()

    def logout(self):
        self.get(config.LOGOUT_URL)
        self.logged_user = None

    def authorize(self, username, password):
        self.assert_http_redirect(self.post(config.LOGIN_URL, {config.USERNAME: username, config.PASSWORD: password}))

    def get(self, url):
        resp = self.c.get(url)
        return resp

    def put(self, url, data={}):
        return self.c.put(url, data)

    def post(self, url, data):
        return self.c.post(url, data)

    def delete(self, url):
        resp = self.c.delete(url)
        return resp

    def assert_http_ok(self, resp):
        return self.assertEqual(resp.status_code, 200)

    def assert_http_created(self, resp):
        return self.assertEqual(resp.status_code, 201)

    def assert_http_accepted(self, resp):
        return self.assertIn(resp.status_code, [202, 204])

    def assert_http_multiple_choices(self, resp):
        return self.assertEqual(resp.status_code, 300)

    def assert_http_redirect(self, resp):
        """
        Ensures the response is returning a HTTP 302.
        """
        return self.assertEqual(resp.status_code, 302)

    def assert_http_see_other(self, resp):
        """
        Ensures the response is returning a HTTP 303.
        """
        return self.assertEqual(resp.status_code, 303)

    def assert_http_not_modified(self, resp):
        """
        Ensures the response is returning a HTTP 304.
        """
        return self.assertEqual(resp.status_code, 304)

    def assert_http_bad_request(self, resp):
        """
        Ensures the response is returning a HTTP 400.
        """
        return self.assertEqual(resp.status_code, 400)

    def assert_http_unauthorized(self, resp):
        """
        Ensures the response is returning a HTTP 401.
        """
        return self.assertEqual(resp.status_code, 401)

    def assert_http_forbidden(self, resp):
        """
        Ensures the response is returning a HTTP 403.
        """
        return self.assertEqual(resp.status_code, 403)

    def assert_http_not_found(self, resp):
        """
        Ensures the response is returning a HTTP 404.
        """
        return self.assertEqual(resp.status_code, 404)

    def assert_http_method_not_allowed(self, resp):
        """
        Ensures the response is returning a HTTP 405.
        """
        return self.assertEqual(resp.status_code, 405)

    def assert_http_conflict(self, resp):
        """
        Ensures the response is returning a HTTP 409.
        """
        return self.assertEqual(resp.status_code, 409)

    def assert_http_gone(self, resp):
        """
        Ensures the response is returning a HTTP 410.
        """
        return self.assertEqual(resp.status_code, 410)

    def assert_http_unprocessable_entity(self, resp):
        """
        Ensures the response is returning a HTTP 422.
        """
        return self.assertEqual(resp.status_code, 422)

    def assert_http_too_many_requests(self, resp):
        """
        Ensures the response is returning a HTTP 429.
        """
        return self.assertEqual(resp.status_code, 429)

    def assert_http_application_error(self, resp):
        """
        Ensures the response is returning a HTTP 500.
        """
        return self.assertEqual(resp.status_code, 500)

    def assert_http_not_implemented(self, resp):
        """
        Ensures the response is returning a HTTP 501.
        """
        return self.assertEqual(resp.status_code, 501)
