import types

from collections.abc import Iterable
from functools import wraps

from inspect import isclass, isfunction, ismethod, getfullargspec, signature

import responses
from django.db import transaction
from django.db.models import Model
from django.db.models.fields import DateField, DateTimeField
from django.utils.functional import cached_property


def is_iterable(data):
    return isinstance(data, Iterable) and not isinstance(data, str)


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


def fill_data_with_source(data, named_data):
    if not named_data:
        return data
    if isinstance(data, dict):
        return {fill_data_with_source(k, named_data): fill_data_with_source(v, named_data) for k, v in data.items()}
    elif isinstance(data, (list, tuple, set)):
        return type(data)(
            (fill_data_with_source(v, named_data) for v in data)
        )
    elif isinstance(data, NamedDataSource):
        try:
            return named_data.get(data.name)
        except KeyError:
            raise AttributeError(f'Source data "{data.name}" was not found in named data')
    else:
        return data


class NamedTestData:

    def __init__(self, **kwargs):
        self.data = dict(**kwargs)

    @property
    def default(self):
        return list(self.data.items())[0][1]

    def get(self, k):
        return self.data[k]

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        raise AttributeError(f'NamedTestData object has no attribute "{item}"')


class NamedDataSource:

    def __init__(self, name):
        self.name = name


def data_provider(function=None, name=None):
    """
    Data provider decorator which prepare data for tests. Data provider should return NamedTestData or name property
    should be set.
    Args:
        function: data provider function or method
        name: name of returned test data

    Returns:
        NamedTestData object
    """

    def _data_provider(function):
        def _decorator(*args, **kwargs):
            return_named_data = kwargs.pop('return_named_data', False)
            returned_data_name = kwargs.pop('returned_data_name', None)
            data = function(*args, **kwargs)
            if return_named_data:
                if not isinstance(data, NamedTestData) and name:
                    data = NamedTestData(**{name: data})
                if returned_data_name:
                    return data.get(returned_data_name)
                else:
                    return data
            else:
                if not isinstance(data, NamedTestData):
                    return data
                elif returned_data_name:
                    return data.get(returned_data_name)
                elif name:
                    return data.get(name)
                else:
                    return data.default
        wrapper = wraps(function)(_decorator)
        wrapper.is_data_provider = True
        return wrapper

    if callable(function):
        return _data_provider(function)
    else:
        return _data_provider


def call(callable, self, data, named_data=None, default_args=None, default_kwargs=None):
    function_or_method_kwargs = {} if default_kwargs is None else dict(**default_kwargs)
    function_or_method_args = [] if default_args is None else list(default_args)

    if 'self' in signature(callable).parameters:
        function_or_method_args.insert(0, self)

    if named_data:
        function_or_method_kwargs.update(
            {
                k: v for k, v in named_data.data.items()
                if k in signature(callable).parameters and k not in function_or_method_kwargs
            }
        )
        return callable(*function_or_method_args, **function_or_method_kwargs)
    else:
        return callable(*function_or_method_args, *data, **function_or_method_kwargs)


def call_test_method(method, self, data, named_data, use_rollback=False):
    if not named_data and isinstance(data, NamedTestData):
        named_data = NamedTestData(**data.data)
    elif named_data and isinstance(data, NamedTestData):
        named_data.data.update(data.data)
    elif named_data and not isinstance(data, NamedTestData):
        named_data = None

    is_data_consumer = getattr(method, 'is_data_consumer', False)
    if use_rollback:
        sid = transaction.savepoint()
    try:
        if is_data_consumer:
            method(self, data=data, named_data=named_data)
        else:
            if hasattr(self, 'set_up_data_consumer'):
                self.tear_up_data_consumer()
            call(method, self, ((data,) if not is_iterable(data) else data), named_data)
    finally:
        if use_rollback:
            transaction.savepoint_rollback(sid)
            responses.reset()
            refresh_model_objects(
                *(data.data.values() if isinstance(data, NamedTestData) else data)
            )
        if not is_data_consumer and hasattr(self, 'tear_down_data_consumer'):
            self.tear_down_data_consumer()


def _copy_named_data(named_data):
    if named_data is None:
        return named_data
    return NamedTestData(**named_data.data)


def _rename_output_data(data, name):
    if not name:
        return data

    if isinstance(name, list):
        assert isinstance(data, (list, tuple, set, NamedTestData)), \
            'Ouput data must be iterable if more output names are set'
        names = name
        values = list(data.data.values()) if isinstance(data, NamedTestData) else list(data)
    else:
        names = [name]
        values = list(data.data.values()) if isinstance(data, NamedTestData) else [data]

    assert len(names) <= len(values), 'More output names than returned values'

    return NamedTestData(**{k: v for k, v in zip(names, values)})


def data_consumer(callable_or_property_or_str, *data_provider_args, **data_provider_kwargs):
    """
    Data provider decorator, allows another callable to provide the data for the test
    Args:
        callable_or_property_or_str: data provider function/method or string name of the data provider method of
                                     the test case class
        *data_provider_args: arguments for the data provider
        **data_provider_kwargs: arguments for the data provider kwargs

    Returns:
        Data created by data provider
    """

    output_name = data_provider_kwargs.pop('_output_name', None)
    def test_decorator(fn):
        def get_data(self, last_data, named_data=None):
            last_args = last_data if last_data else ()
            if isinstance(last_args, NamedTestData):
                last_args = (last_args.default,)
            elif not is_iterable(last_args):
                last_args = (last_args,)

            callable_or_property = (
                getattr(self, callable_or_property_or_str)
                if isinstance(callable_or_property_or_str, str) else callable_or_property_or_str
            )

            if ismethod(callable_or_property) or isclass(callable_or_property) or isfunction(callable_or_property):
                if getattr(callable_or_property, 'is_data_provider', False):
                    data_provider_kwargs['return_named_data'] = True
                data = call(
                    callable_or_property,
                    self,
                    last_args,
                    named_data,
                    fill_data_with_source(data_provider_args, named_data),
                    fill_data_with_source(data_provider_kwargs, named_data)
                )
            else:
                assert isinstance(callable_or_property, (list, tuple, set, types.GeneratorType)), (
                    'Only list, tuple, set, generator, function or method can be used with data_consumer'
                )
                data = callable_or_property

            if isinstance(data, (list, tuple, set, types.GeneratorType)):
                for value in data:
                    value = _rename_output_data(value, output_name)
                    if not isinstance(value, NamedTestData):
                        value = list(last_args) + (list(value) if isinstance(value, (list, tuple, set)) else [value])
                    yield value, True
            else:
                yield _rename_output_data(data, output_name), False

        def repl(self, data=None, named_data=None):
            for data, use_rollback in get_data(self, data, named_data):
                call_test_method(fn, self, data, _copy_named_data(named_data), use_rollback=use_rollback)

        wrapper = wraps(fn)(repl)
        wrapper.is_data_consumer = True
        wrapper.get_data = get_data
        wrapper.fn = fn
        return wrapper
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
