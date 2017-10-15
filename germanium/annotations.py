from __future__ import unicode_literals

import collections
from functools import wraps

import six

import responses
from django.db import transaction
from django.db.models.fields import DateField, DateTimeField


def login(function=None, users_generator='get_user', **users_kwargs):
    """Login decorator usage: @login(user_data)"""

    def _login(function):
        def _decorator(self, *args, **kwargs):
            if isinstance(users_generator, six.string_types):
                users = getattr(self, users_generator)(**users_kwargs)
            else:
                users = users_generator(self, **users_kwargs)

            if not isinstance(users, (list, tuple)):
                users = (users,)

            for user in users:
                self.login(user)
                function(self, *args, **kwargs)
                self.logout()
        return wraps(function)(_decorator)

    if function:
        return _login(function)
    return _login


def login_all(cls=None, **user_kwargs):
    """Login decorator for all methods inside test usage: @login(user_data)"""

    def _login_all(cls):
        for attr, val in cls.__dict__.items():
            if callable(val) and attr.startswith("test_"):
                setattr(cls, attr, login(**user_kwargs)(val))
        return cls

    if cls:
        return _login_all(cls)
    return _login_all


def data_provider(fn_data_provider_or_str, *data_provider_args, **data_provider_kwargs):
    """Data provider decorator, allows another callable to provide the data for the test"""

    def test_decorator(fn):

        def get_data(self):
            if isinstance(fn_data_provider_or_str, six.string_types):
                provider_args = data_provider_args
                method_or_property = getattr(self, fn_data_provider_or_str)
            else:
                provider_args = (self,) + data_provider_args
                method_or_property = fn_data_provider_or_str

            return (
                method_or_property if not hasattr(method_or_property, '__call__')
                else method_or_property(*provider_args, **data_provider_kwargs)
            )

        def repl(self, *args):
            data = get_data(self)
            if not isinstance(data, collections .Iterable):
                data = (data,)
            for i in data:
                sid = transaction.savepoint()
                try:
                    if isinstance(i, collections.Iterable) and not isinstance(i, six.string_types):
                        fn(self, *i)
                    else:
                        fn(self, i)
                except AssertionError:
                    raise
                finally:
                    transaction.savepoint_rollback(sid)
                    responses.reset()
        return wraps(fn)(repl)
    return test_decorator


def turn_off_auto_now(model_class, field_name):

    def _turn_off_auto_now(function):
        def _decorator(self, *args, **kwargs):
                field = model_class._meta.get_field(field_name)
                if not isinstance(field, (DateField, DateTimeField)):
                    raise RuntimeError('Field %s must be DateField or DateTimeField type') % field_name
                if not field.auto_now:
                    raise RuntimeError('Field %s must have set auto_no to True') % field_name
                field.auto_now = False
                try:
                    function(self, *args, **kwargs)
                except AssertionError:
                    raise
                finally:
                    field.auto_now = True
        return wraps(function)(_decorator)

    return _turn_off_auto_now
