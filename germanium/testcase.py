import time

from django.test.testcases import LiveServerTestCase
from django.conf import settings

from django_selenium.testcases import MyDriver

from selenium import webdriver

from germanium import config
from germanium.auth import AuthTestCaseMixin
from germanium.asserts import GermaniumAssertMixin

from selenium.common.exceptions import WebDriverException


SELENIUM_TESTS_WAIT = getattr(settings, 'SELENIUM_TESTS_WAIT', 0.1)


class ConfigurableWaitDriver(MyDriver):

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


class GermaniumTestCase(AuthTestCaseMixin, GermaniumAssertMixin, LiveServerTestCase):

    is_logged = False
    app_path = ''

    @classmethod
    def setUpClass(cls):
        cls.set_up_class()

    @classmethod
    def set_up_class(cls):
        super(GermaniumTestCase, cls).setUpClass()

    def setUp(self):
        super(GermaniumTestCase, self).setUp()
        self.set_up()

    def set_up(self):
        self.driver = ConfigurableWaitDriver()
        self.driver.live_server_url = self.live_server_url

    def tearDown(self):
        self.tear_down()
        super(GermaniumTestCase, self).tearDown()

    def tear_down(self):
        self.driver.quit()

    @classmethod
    def tearDownClass(cls):
        cls.tear_down_class()

    @classmethod
    def tear_down_class(cls):
        super(GermaniumTestCase, cls).tearDownClass()

    def open(self, url):
        self.driver.get("%s%s" % (self.live_server_url, url))

    def open_and_wait(self, url, timeout=1):
        self.driver.get("%s%s" % (self.live_server_url, url))
        time.sleep(timeout)

    def go(self, url=''):
        self.open(self.app_path + url)

    def go_and_wait(self, url='', timeout=1):
        print self.app_path + url
        self.open_and_wait(self.app_path + url, timeout)

    def logout(self):
        self.open(config.LOGOUT_URL)
        self.is_logged = False

    def authorize(self, username, password):
        self.open('/')
        self.type('input#id_' + config.USERNAME, username)
        self.type('input#id_' + config.PASSWORD, password)
        self.click(config.BTN_SUBMIT)
        time.sleep(1)

