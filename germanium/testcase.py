import time

from django.test.testcases import LiveServerTestCase

from selenium import webdriver

from germanium import config
from germanium.auth import AuthTestCaseMixin
from germanium.asserts import GermaniumAssertMixin


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
        self.set_up()

    def set_up(self):
        super(GermaniumTestCase, self).setUp()
        self.driver = webdriver.PhantomJS(config.PHANTOM_JS_BIN)

    def tearDown(self):
        self.tear_down()

    def tear_down(self):
        time.sleep(1)
        self.driver.quit()
        super(GermaniumTestCase, self).tearDown()

    @classmethod
    def tearDownClass(cls):
        cls.tear_down_class()

    @classmethod
    def tear_down_class(cls):
        super(GermaniumTestCase, cls).tearDownClass()

    def open(self, url):
        self.driver.get("%s%s" % (self.live_server_url, url))

    def open_and_wait(self, url, timeout=3):
        self.driver.get("%s%s" % (self.live_server_url, url))
        time.sleep(timeout)

    def go(self, url=''):
        self.open(self.app_path + url)

    def go_and_wait(self, url='', timeout=3):
        self.open_and_wait(self.app_path + url, timeout)

    def login(self, email=None, password=None, role=None, is_superuser=True):
        if email is None:
            email = self.email

        if self.is_logged:
            self.logout()

        self.authorize(email, password)
        self.is_logged = True

    def logout(self):
        self.open(config.LOGOUT_URL)
        self.is_logged = False

    def authorize(self, username, password):
        self.open('/')
        self.type('input#id_' + config.USERNAME, username)
        self.type('input#id_' + config.PASSWORD, password)
        self.click(config.BTN_SUBMIT)
