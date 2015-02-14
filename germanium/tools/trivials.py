from django_nose.tools import *

from exceptions import AssertionError


def assert_is_none(expr, msg=None):
    assert_equals(expr, None, msg)

def assert_is_not_none(expr, msg=None):
    assert_not_equals(expr, None, msg)

def fail(msg=None):
    raise AssertionError(msg)