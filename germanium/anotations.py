import collections
import six

from django.utils.unittest.compatibility import wraps


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
        for attr, val in cls.__dict__.iteritems():
            if callable(val) and attr.startswith("test_"):
                setattr(cls, attr, login(**user_kwargs)(val))
        return cls

    if cls:
        return _login_all(cls)
    return _login_all


def data_provider(fn_data_provider_or_str, *data_provider_args, **data_provider_kwargs):
    """Data provider decorator, allows another callable to provide the data for the test"""

    def test_decorator(fn):
        def repl(self, *args):
            if isinstance(fn_data_provider_or_str, six.string_types):
                data = getattr(self, fn_data_provider_or_str)(*data_provider_args, **data_provider_kwargs)
            else:
                data = fn_data_provider_or_str(self, *data_provider_args, **data_provider_kwargs)

            for i in data:
                try:
                    if isinstance(i, collections.Iterable):
                        fn(self, *i)
                    else:
                        fn(self, i)
                except AssertionError:
                    print "Assertion error caught with data set ", i
                    raise
        return repl
    return test_decorator
