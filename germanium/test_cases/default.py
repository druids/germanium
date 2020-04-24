import types

from django.conf import settings
from django.test.testcases import TestCase, SimpleTestCase

from germanium.config import TEST_ALL_DATABASES


class GermaniumSimpleTestCaseMixin:

    if TEST_ALL_DATABASES:
        databases = list(settings.DATABASES.keys())

    @classmethod
    def setUpClass(cls):
        super(GermaniumSimpleTestCaseMixin, cls).setUpClass()
        cls.set_up_class()

    @classmethod
    def set_up_class(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        super(GermaniumSimpleTestCaseMixin, cls).tearDownClass()
        cls.tear_down_class()

    @classmethod
    def tear_down_class(cls):
        pass

    def setUp(self):
        super(GermaniumSimpleTestCaseMixin, self).setUp()
        self.set_up()

    def set_up(self):
        pass

    def tearDown(self):
        super(GermaniumSimpleTestCaseMixin, self).tearDown()
        self.tear_down()

    def tear_down(self):
        pass


class GermaniumTestCaseMixin(GermaniumSimpleTestCaseMixin):

    if getattr(settings, 'GERMANIUM_FIXTURES', None):
        fixtures = getattr(settings, 'GERMANIUM_FIXTURES', None)


class GermaniumTestCase(GermaniumTestCaseMixin, TestCase):
    pass


class GermaniumSimpleTestCase(GermaniumSimpleTestCaseMixin, SimpleTestCase):
    pass
