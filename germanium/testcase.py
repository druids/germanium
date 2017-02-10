from __future__ import unicode_literals

import time
import types

from germanium import config
from germanium.auth import AuthTestCaseMixin
from germanium.patch import patch_broken_pipe_error
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test.testcases import TestCase
from django_selenium import settings as selenium_settings
from django_selenium.testcases import MyDriver

SELENIUM_TESTS_WAIT = getattr(settings, 'SELENIUM_TESTS_WAIT', 0.1)
PHANTOM_JS_BIN = getattr(settings, 'PHANTOM_JS_BIN', None)


class ConfigurableWaitDriver(MyDriver):

    def __init__(self):
        driver = getattr(webdriver, selenium_settings.SELENIUM_DRIVER, None)
        assert driver, "settings.SELENIUM_DRIVER contains non-existing driver"
        if driver is webdriver.PhantomJS and PHANTOM_JS_BIN:
            self.driver = driver(PHANTOM_JS_BIN)
            self.live_server_url = 'http://%s:%s' % (selenium_settings.SELENIUM_TESTSERVER_HOST,
                                                     str(selenium_settings.SELENIUM_TESTSERVER_PORT))
            self.text = ''
        else:
            super(ConfigurableWaitDriver, self).__init__()

    def _wait_for_page_source(self):
        try:
            page_source = self.page_source
            time.sleep(SELENIUM_TESTS_WAIT)
            while page_source != self.page_source:
                page_source = self.page_source
                time.sleep(SELENIUM_TESTS_WAIT)
            self.update_text()
        except WebDriverException:
            pass


def convert_to_test_obj(obj):
    obj.change_and_save = types.MethodType(change_and_save, obj)
    obj.reload = types.MethodType(reload, obj)
    return obj


def change_and_save(self, save_kwargs=None, **kwargs):
    save_kwargs = {} if save_kwargs is None else save_kwargs
    for attr, val in kwargs.items():
        setattr(self, attr, val)
    self.save(**save_kwargs)
    return self


def reload(self):
    if self.pk:
        self = self.__class__.objects.get(pk=self.pk)
    convert_to_test_obj(self)
    return self


class GermaniumTestCaseMixin(object):
    if getattr(settings, 'GERMANIUM_FIXTURES', None):
        fixtures = getattr(settings, 'GERMANIUM_FIXTURES', None)


class GermaniumTestCase(GermaniumTestCaseMixin, TestCase):
    pass


class GermaniumLiveServerTestCase(GermaniumTestCaseMixin, AuthTestCaseMixin, StaticLiveServerTestCase):

    is_logged = False

    @classmethod
    def setUpClass(cls):
        cls.set_up_class()

    @classmethod
    def set_up_class(cls):
        patch_broken_pipe_error()
        super(GermaniumLiveServerTestCase, cls).setUpClass()

    def setUp(self):
        super(GermaniumLiveServerTestCase, self).setUp()
        self.set_up()

    def set_up(self):
        self.driver = ConfigurableWaitDriver()
        self.driver.live_server_url = self.live_server_url
        self.driver.set_window_size(*config.WINDOW_SIZE)

    def tearDown(self):
        self.tear_down()
        super(GermaniumLiveServerTestCase, self).tearDown()

    def tear_down(self):
        self.driver.quit()
        time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        cls.tear_down_class()

    @classmethod
    def tear_down_class(cls):
        super(GermaniumLiveServerTestCase, cls).tearDownClass()

    def open(self, url=''):
        self.driver.open_url(url)

    def logout(self):
        self.open(config.LOGOUT_URL)
        self.is_logged = False

    def authorize(self, username, password):
        self.open('/')
        self.type('input#id_' + config.USERNAME, username)
        self.type('input#id_' + config.PASSWORD, password)
        self.click(config.BTN_SUBMIT)
        time.sleep(1)


class ModelTestCase(GermaniumTestCase):

    factory_class = None

    def inst_data_provider(self, **inst_kwargs):
        factory_class = inst_kwargs.pop('factory_class', self.factory_class)
        if 'pk' in inst_kwargs:
            inst = factory_class._get_model_class().objects.get(pk=inst_kwargs.get('pk'))
        else:
            inst = factory_class(**inst_kwargs)
        convert_to_test_obj(inst)
        return inst

    def insts_data_provider(self, count=10, **inst_kwargs):
        insts = []
        for _ in range(count):
            insts.append(self.inst_data_provider(**inst_kwargs))
        return insts
