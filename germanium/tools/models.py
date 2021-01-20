from .trivials import assert_equal, assert_true, assert_false


def get_pks(iterable):
    return [obj.pk for obj in iterable]


def assert_iterable_equal(first, second, msg=None):
    assert_equal(set(first), set(second), msg)


def assert_qs_exists(qs):
    assert_true(qs.exists())


def assert_qs_not_exists(qs):
    assert_false(qs.exists())


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


def assert_equal_model_fields(model_instance, **field_values):
    for field_name, field_value in field_values.items():
        assert_equal(getattr(model_instance, field_name), field_value, 'Invalid value of "{}"'.format(field_name))
