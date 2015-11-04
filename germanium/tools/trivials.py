from __future__ import unicode_literals

from django_nose.tools import *


def assert_is_none(expr, msg=None):
    assert_equals(expr, None, msg)


def assert_is_not_none(expr, msg=None):
    assert_not_equals(expr, None, msg)


def fail(msg=None):
    raise AssertionError(msg)
