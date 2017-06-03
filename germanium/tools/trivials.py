"""
Provides Nose and Django test case assert functions
"""

from __future__ import unicode_literals

from nose.tools import (assert_equal, assert_true, assert_false, assert_in, assert_not_in, assert_raises,
                        assert_not_equal, assert_is, assert_is_instance, assert_greater, assert_less,
                        assert_almost_equal, assert_not_almost_equal, assert_greater_equal, assert_less_equal,
                        assert_not_is_instance, assert_list_equal, assert_tuple_equal, assert_set_equal,
                        assert_dict_equal, assert_sequence_equal, assert_multi_line_equal, assert_is_none,
                        assert_is_not_none, assert_equals)


def fail(msg=None):
    raise AssertionError(msg)
