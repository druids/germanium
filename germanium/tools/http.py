from __future__ import unicode_literals

from .trivials import *


def assert_http_ok(resp, msg=None):
    return assert_equal(resp.status_code, 200, msg)


def assert_http_created(resp, msg=None):
    return assert_equal(resp.status_code, 201, msg)


def assert_http_accepted(resp, msg=None):
    return assert_in(resp.status_code, [202, 204], msg)


def assert_http_multiple_choices(resp, msg=None):
    return assert_equal(resp.status_code, 300, msg)


def assert_http_redirect(resp, msg=None):
    """
    Ensures the response is returning a HTTP 302.
    """
    return assert_equal(resp.status_code, 302, msg)


def assert_http_see_other(resp, msg=None):
    """
    Ensures the response is returning a HTTP 303.
    """
    return assert_equal(resp.status_code, 303, msg)


def assert_http_not_modified(resp, msg=None):
    """
    Ensures the response is returning a HTTP 304.
    """
    return assert_equal(resp.status_code, 304, msg)


def assert_http_bad_request(resp, msg=None):
    """
    Ensures the response is returning a HTTP 400.
    """
    return assert_equal(resp.status_code, 400, msg)


def assert_http_unauthorized(resp, msg=None):
    """
    Ensures the response is returning a HTTP 401.
    """
    return assert_equal(resp.status_code, 401, msg)


def assert_http_forbidden(resp, msg=None):
    """
    Ensures the response is returning a HTTP 403.
    """
    return assert_equal(resp.status_code, 403, msg)


def assert_http_not_found(resp, msg=None):
    """
    Ensures the response is returning a HTTP 404.
    """
    return assert_equal(resp.status_code, 404, msg)


def assert_http_method_not_allowed(resp, msg=None):
    """
    Ensures the response is returning a HTTP 405.
    """
    return assert_equal(resp.status_code, 405, msg)


def assert_http_conflict(resp, msg=None):
    """
    Ensures the response is returning a HTTP 409.
    """
    return assert_equal(resp.status_code, 409, msg)


def assert_http_gone(resp, msg=None):
    """
    Ensures the response is returning a HTTP 410.
    """
    return gt.assert_equal(resp.status_code, 410, msg)


def assert_http_unprocessable_entity(resp, msg=None):
    """
    Ensures the response is returning a HTTP 422.
    """
    return assert_equal(resp.status_code, 422, msg)


def assert_http_too_many_requests(resp, msg=None):
    """
    Ensures the response is returning a HTTP 429.
    """
    return assert_equal(resp.status_code, 429, msg)


def assert_http_application_error(resp, msg=None):
    """
    Ensures the response is returning a HTTP 500.
    """
    return assert_equal(resp.status_code, 500, msg)


def assert_http_not_implemented(resp, msg=None):
    """
    Ensures the response is returning a HTTP 501.
    """
    return assert_equal(resp.status_code, 501, msg)


def assert_http_service_unavailable(resp, msg=None):
    """
    Ensures the response is returning a HTTP 503.
    """
    return gt.assert_equal(resp.status_code, 503, msg)    
