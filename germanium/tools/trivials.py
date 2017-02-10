"""
Provides Nose and Django test case assert functions
"""

from __future__ import unicode_literals

from django.test.testcases import TransactionTestCase


import re

## Python

from nose import tools
for t in dir(tools):
    if t.startswith('assert_') or t in ('ok_', 'eq_'):
        vars()[t] = getattr(tools, t)

del tools
del t

## Django

camelcase = re.compile('([a-z][A-Z]|[A-Z][a-z])')

def insert_underscore(m):
    a, b = m.group(0)
    if b.islower():
        return '_{}{}'.format(a, b)
    else:
        return '{}_{}'.format(a, b)

def pep8(name):
    return camelcase.sub(insert_underscore, name).lower()

class Dummy(TransactionTestCase):
    def nop():
        pass
_t = Dummy('nop')

for at in [ at for at in dir(_t)
            if at.startswith('assert') and not '_' in at ]:
    pepd = pep8(at)
    vars()[pepd] = getattr(_t, at)

del re
del insert_underscore
del camelcase
del Dummy
del TransactionTestCase
del _t
del at
del pep8
del pepd


def assert_is_none(expr, msg=None):
    assert_equal(expr, None, msg)


def assert_is_not_none(expr, msg=None):
    assert_not_equal(expr, None, msg)


def fail(msg=None):
    raise AssertionError(msg)
