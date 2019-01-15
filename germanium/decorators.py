import collections
from functools import wraps

from inspect import isclass, isfunction, ismethod, getfullargspec

import responses
from django.db import transaction
from django.db.models import Model
from django.db.models.fields import DateField, DateTimeField
from django.utils.functional import cached_property


def is_iterable(data):
    return isinstance(data, collections.Iterable) and not isinstance(data, str)


def refresh_model_object(obj):
    obj.refresh_from_db()
    for key, value in obj.__class__.__dict__.items():
        if isinstance(value, cached_property):
            obj.__dict__.pop(key, None)


def refresh_model_objects(*data):
    [refresh_model_object(obj) for obj in data if isinstance(obj, Model) and obj.pk]


def login(function=None, users_generator='get_user', **users_kwargs):
    """Login decorator usage: @login(user_data)"""

    def _login(function):
        def _decorator(self, *args, **kwargs):
            if isinstance(users_generator, str):
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


def data_provider(callable_or_property_or_str, *data_provider_args, **data_provider_kwargs):
    """Data provider decorator, allows another callable to provide the data for the test"""

    def test_decorator(fn):

        def get_data(self, *args):
            callable_or_property = (
                getattr(self, callable_or_property_or_str)
                if isinstance(callable_or_property_or_str, str) else callable_or_property_or_str
            )
            if (isfunction(callable_or_property) and next(iter(getfullargspec(callable_or_property).args),
                                                          None) == 'self'):
                return callable_or_property(self, *data_provider_args, *args, **data_provider_kwargs)
            elif ismethod(callable_or_property) or isclass(callable_or_property) or isfunction(callable_or_property):
                return callable_or_property(*data_provider_args, *args, **data_provider_kwargs)
            else:
                return [list(args) + list(val if is_iterable(val) else [val]) for val in callable_or_property]

        def repl(self, *args):
            data = get_data(self, *args)
            if not is_iterable(data):
                data = (data,)
            for fn_args in data:
                if not is_iterable(fn_args):
                    fn_args = [fn_args]
                if getattr(fn, 'data_provider', False):
                    fn(self, *fn_args)
                else:
                    sid = transaction.savepoint()
                    try:
                        fn(self, *fn_args)
                    except AssertionError:
                        raise
                    finally:
                        transaction.savepoint_rollback(sid)
                        responses.reset()
                        refresh_model_objects(*fn_args)
            repl.data_provider = True
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
