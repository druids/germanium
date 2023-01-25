from django.core.exceptions import ObjectDoesNotExist
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.models.constants import LOOKUP_SEP
from django.test.utils import CaptureQueriesContext
from django.contrib.contenttypes.models import ContentType

from .trivials import assert_equal, assert_true, assert_false


def get_pks(iterable):
    return [obj.pk for obj in iterable]


def assert_iterable_equal(first, second, msg=None):
    assert_equal(set(first), set(second), msg)


def assert_qs_exists(qs, msg=None):
    assert_true(qs.exists(), msg)


def assert_qs_not_exists(qs, msg=None):
    assert_false(qs.exists(), msg)


def assert_qs_contains(qs, obj, msg=None):
    assert_equal(
        set(qs.filter(pk__in=get_pks(obj if isinstance(obj, (set, list, tuple)) else {obj}))),
        set(obj) if isinstance(obj, (set, list, tuple)) else {obj},
        msg
    )


def assert_qs_not_contains(qs, obj, msg=None):
    assert_false(
        qs.filter(pk__in=get_pks(obj if isinstance(obj, (set, list, tuple)) else {obj})).exists(),
        msg
    )


def model_instance_getattr(instance, key):
    try:
        return getattr(instance, key)
    except ObjectDoesNotExist:
        return None


def get_value_from_model_instance(instance, field_name):
    if LOOKUP_SEP in field_name:
        current_field_name, next_field_name = field_name.split(LOOKUP_SEP, 1)
        value = model_instance_getattr(instance, current_field_name)
        if value is None:
            raise AttributeError('Value cannot be get from instance')
        return get_value_from_model_instance(value, next_field_name)
    else:
        return model_instance_getattr(instance, field_name)


def assert_equal_model_fields(instance, refresh_from_db=False, **field_values):
    if refresh_from_db:
        instance.refresh_from_db()
    for field_name, field_value in field_values.items():
        assert_equal(
            get_value_from_model_instance(instance, field_name), field_value, 'Invalid value of "{}"'.format(field_name)
        )


class _AssertNumQueriesContext(CaptureQueriesContext):

    def __init__(self, num, connection, clear_content_type_cache):
        self.num = num
        self.clear_content_type_cache = clear_content_type_cache
        super().__init__(connection)

    def __enter__(self):
        if self.clear_content_type_cache:
            ContentType.objects.clear_cache()
        super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
        if exc_type is not None:
            return
        executed = len(self)
        assert_equal(
            executed, self.num,
            "%d queries executed, %d expected\nCaptured queries were:\n%s" % (
                executed, self.num,
                '\n'.join(
                    '%d. %s' % (i, query['sql']) for i, query in enumerate(self.captured_queries, start=1)
                )
            )
        )


def assert_num_queries(num, func=None, *args, using=DEFAULT_DB_ALIAS, clear_content_type_cache=False, **kwargs):
    conn = connections[using]

    context = _AssertNumQueriesContext(num, conn, clear_content_type_cache)

    if func is None:
        return context

    with context:
        func(*args, **kwargs)
