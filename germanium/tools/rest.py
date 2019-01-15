import json

from django.utils.encoding import force_text

from .trivials import assert_true, assert_equal, assert_in, fail
from .http import assert_http_ok, assert_http_created


def assert_valid_JSON(data, msg='Json is not valid'):
    """
    Given the provided ``data`` as a string, ensures that it is valid JSON &
    can be loaded properly.
    """
    try:
        json.loads(force_text(data))
    except:
        fail(msg)


def assert_valid_JSON_response(resp, msg=None):
    """
    Given a ``HttpResponse`` coming back from using the ``client``, assert that
    you get back:

    * An HTTP 200
    * The correct content-type (``application/json``)
    * The content is valid JSON
    """
    assert_http_ok(resp, msg)
    assert_true(resp['Content-Type'].startswith('application/json'), msg)
    assert_valid_JSON(resp.content, msg)


def assert_valid_JSON_created_response(resp, msg=None):
    """
    Given a ``HttpResponse`` coming back from using the ``client``, assert that
    you get back:

    * An HTTP 201
    * The correct content-type (``application/json``)
    * The content is valid JSON
    """
    assert_http_created(resp, msg)
    assert_true(resp['Content-Type'].startswith('application/json'), msg)
    assert_valid_JSON(resp.content, msg)


def assert_keys(data, expected):
    """
    This method ensures that the keys of the ``data`` match up to the keys of
    ``expected``.

    It covers the (extremely) common case where you want to make sure the keys of
    a response match up to what is expected. This is typically less fragile than
    testing the full structure, which can be prone to data changes.
    """
    assert_equal(set(data.keys()), set(expected))
