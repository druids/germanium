from __future__ import unicode_literals

import json

from django.utils.encoding import force_text

from .trivials import assert_true, assert_equal, assert_in, fail
from .http import assert_http_ok


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
