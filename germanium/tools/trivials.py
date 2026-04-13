"""
Provides Django test case assert functions
"""

import unittest
from contextlib import contextmanager

_tc = unittest.TestCase()

assert_equal = _tc.assertEqual
assert_true = _tc.assertTrue
assert_false = _tc.assertFalse
assert_in = _tc.assertIn
assert_not_in = _tc.assertNotIn
assert_raises = _tc.assertRaises
assert_not_equal = _tc.assertNotEqual
assert_is = _tc.assertIs
assert_is_instance = _tc.assertIsInstance
assert_greater = _tc.assertGreater
assert_less = _tc.assertLess
assert_almost_equal = _tc.assertAlmostEqual
assert_not_almost_equal = _tc.assertNotAlmostEqual
assert_greater_equal = _tc.assertGreaterEqual
assert_less_equal = _tc.assertLessEqual
assert_not_is_instance = _tc.assertNotIsInstance
assert_list_equal = _tc.assertListEqual
assert_tuple_equal = _tc.assertTupleEqual
assert_set_equal = _tc.assertSetEqual
assert_dict_equal = _tc.assertDictEqual
assert_sequence_equal = _tc.assertSequenceEqual
assert_multi_line_equal = _tc.assertMultiLineEqual
assert_is_none = _tc.assertIsNone
assert_is_not_none = _tc.assertIsNotNone
assert_equals = _tc.assertEqual
assert_logs = _tc.assertLogs

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
        raise fail("{} raised".format(exc_type.__name__))


def assert_length_equal(iterable, expected_length, msg=None):
    assert_equal(len(iterable), expected_length, msg)


class AllEqual:

    def __eq__(self, obj):
        return True


class NotNoneEqual:

    def __eq__(self, obj):
        return obj is not None


all_eq_obj = AllEqual()
not_none_eq_obj = NotNoneEqual()
