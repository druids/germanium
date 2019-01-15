import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from django_selenium import settings as selenium_settings
from django_selenium.testcases import MyDriver

from germanium import config
from germanium.patch import patch_broken_pipe_error

from .auth import AuthTestCaseMixin
from .default import GermaniumTestCaseMixin


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


class GermaniumLiveServerTestCase(GermaniumTestCaseMixin, AuthTestCaseMixin, StaticLiveServerTestCase):

    is_logged = False

    @classmethod
    def set_up_class(cls):
        super(GermaniumLiveServerTestCase, cls).set_up_class()
        patch_broken_pipe_error()

    def tear_down(self):
        super(GermaniumLiveServerTestCase, self).tear_down()
        self.driver.quit()
        time.sleep(2)

    def set_up(self):
        super(GermaniumLiveServerTestCase, cls).set_up()
        self.driver = ConfigurableWaitDriver()
        self.driver.live_server_url = self.live_server_url
        self.driver.set_window_size(*config.WINDOW_SIZE)

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
