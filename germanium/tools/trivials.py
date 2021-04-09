"""
Provides Nose and Django test case assert functions
"""
from contextlib import contextmanager

from nose.tools import (
    assert_equal, assert_true, assert_false, assert_in, assert_not_in, assert_raises, assert_not_equal, assert_is,
    assert_is_instance, assert_greater, assert_less, assert_almost_equal, assert_not_almost_equal, assert_greater_equal,
    assert_less_equal, assert_not_is_instance, assert_list_equal, assert_tuple_equal, assert_set_equal,
    assert_dict_equal, assert_sequence_equal, assert_multi_line_equal, assert_is_none, assert_is_not_none,
    assert_equals, assert_logs
)

from germanium import config


if config.TURN_OFF_MAX_DIFF:
    assert_equal.__self__.maxDiff = None


def fail(msg=None):
    raise AssertionError(msg)


@contextmanager
def assert_not_raises(exc_type, func=None, *args, **kwargs):
    try:
        if func:
            func(*args, **kwargs)
        yield None
    except exc_type:
        raise fail('{} raised'.format(exc_type.__name__))
