from urllib.parse import urlencode

from django.utils.encoding import force_text

from .trivials import assert_equal, assert_in


def get_full_path(*paths):
    string_paths = (force_text(path) for path in paths)
    full_path = '/'.join((path[:-1] if path.endswith('/') else path for path in string_paths))
    return full_path if full_path.endswith('/') else full_path + '/'


def build_url(*paths, **querystring_dict):
    return (
        '{}?{}'.format(get_full_path(*paths), urlencode(querystring_dict))
        if querystring_dict else get_full_path(*paths)
    )


def assert_http_ok(resp, msg=None):
    """
    Ensures the response is returning a HTTP 200.
    """
    return assert_equal(resp.status_code, 200, resp.content if msg is None else msg)


def assert_http_created(resp, msg=None):
    """
    Ensures the response is returning a HTTP 201.
    """
    return assert_equal(resp.status_code, 201, resp.content if msg is None else msg)


def assert_http_accepted(resp, msg=None):
    """
    Ensures the response is returning a HTTP 202 or 204.
    """
    return assert_in(resp.status_code, [202, 204], resp.content if msg is None else msg)


def assert_http_multiple_choices(resp, msg=None):
    """
    Ensures the response is returning a HTTP 300.
    """
    return assert_equal(resp.status_code, 300, resp.content if msg is None else msg)


def assert_http_redirect(resp, msg=None):
    """
    Ensures the response is returning a HTTP 302.
    """
    return assert_equal(resp.status_code, 302, resp.content if msg is None else msg)


def assert_http_see_other(resp, msg=None):
    """
    Ensures the response is returning a HTTP 303.
    """
    return assert_equal(resp.status_code, 303, resp.content if msg is None else msg)


def assert_http_not_modified(resp, msg=None):
    """
    Ensures the response is returning a HTTP 304.
    """
    return assert_equal(resp.status_code, 304, resp.content if msg is None else msg)


def assert_http_bad_request(resp, msg=None):
    """
    Ensures the response is returning a HTTP 400.
    """
    return assert_equal(resp.status_code, 400, resp.content if msg is None else msg)


def assert_http_unauthorized(resp, msg=None):
    """
    Ensures the response is returning a HTTP 401.
    """
    return assert_equal(resp.status_code, 401, resp.content if msg is None else msg)


def assert_http_forbidden(resp, msg=None):
    """
    Ensures the response is returning a HTTP 403.
    """
    return assert_equal(resp.status_code, 403, resp.content if msg is None else msg)


def assert_http_not_found(resp, msg=None):
    """
    Ensures the response is returning a HTTP 404.
    """
    return assert_equal(resp.status_code, 404, resp.content if msg is None else msg)


def assert_http_method_not_allowed(resp, msg=None):
    """
    Ensures the response is returning a HTTP 405.
    """
    return assert_equal(resp.status_code, 405, resp.content if msg is None else msg)


def assert_http_conflict(resp, msg=None):
    """
    Ensures the response is returning a HTTP 409.
    """
    return assert_equal(resp.status_code, 409, resp.content if msg is None else msg)


def assert_http_gone(resp, msg=None):
    """
    Ensures the response is returning a HTTP 410.
    """
    return assert_equal(resp.status_code, 410, resp.content if msg is None else msg)


def assert_http_unprocessable_entity(resp, msg=None):
    """
    Ensures the response is returning a HTTP 422.
    """
    return assert_equal(resp.status_code, 422, resp.content if msg is None else msg)


def assert_http_too_many_requests(resp, msg=None):
    """
    Ensures the response is returning a HTTP 429.
    """
    return assert_equal(resp.status_code, 429, resp.content if msg is None else msg)


def assert_http_application_error(resp, msg=None):
    """
    Ensures the response is returning a HTTP 500.
    """
    return assert_equal(resp.status_code, 500, resp.content if msg is None else msg)


def assert_http_not_implemented(resp, msg=None):
    """
    Ensures the response is returning a HTTP 501.
    """
    return assert_equal(resp.status_code, 501, resp.content if msg is None else msg)


def assert_http_bad_gateway(resp, msg=None):
    """
    Ensures the response is returning a HTTP 502.
    """
    return assert_equal(resp.status_code, 502, resp.content if msg is None else msg)


def assert_http_service_unavailable(resp, msg=None):
    """
    Ensures the response is returning a HTTP 503.
    """

    return assert_equal(resp.status_code, 503, resp.content if msg is None else msg)


def assert_http_gateway_timeout(resp, msg=None):
    """
    Ensures the response is returning a HTTP 504.
    """
    return assert_equal(resp.status_code, 504, resp.content if msg is None else msg)
