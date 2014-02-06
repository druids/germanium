import time

import config
from asserts import Assert
from django_selenium.testcases import MyDriver

from selenium.common.exceptions import WebDriverException

from selenium.webdriver.common.action_chains import ActionChains


SELENIUM_TESTS_WAIT = config.SELENIUM_TESTS_WAIT

SELENIUM_DISPLAY_DIMENSION = getattr(config, 'SELENIUM_DISPLAY_DIMENSION', (1440, 900))


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


class GermaniumTestCase(Assert):
    main_wrapper = ''
    logged_user = None

    @classmethod
    def setUpClass(cls):
        if settings.SELENIUM_RUN_IN_BACKGROUND:
            from pyvirtualdisplay import Display
            cls.display = Display(visible=0, size=SELENIUM_DISPLAY_DIMENSION)
            cls.display.start()

        super(GermaniumTestCase, cls).setUpClass()

    def setUp(self):
        super(GermaniumTestCase, self).setUp()
        self.email = 'test_user@test.cz'
        self.driver = ConfigurableWaitDriver()
        self.driver.set_window_size(SELENIUM_DISPLAY_DIMENSION[0], SELENIUM_DISPLAY_DIMENSION[1])
        self.driver.live_server_url = self.live_server_url

    def tearDown(self):
        time.sleep(1)
        self.driver.quit()
        super(GermaniumTestCase, self).tearDown()

    @classmethod
    def tearDownClass(cls):
        if settings.SELENIUM_RUN_IN_BACKGROUND:
            cls.display.stop()
        super(GermaniumTestCase, cls).tearDownClass()

    def get_logged_user(self, email, password, role, is_superuser):
        return None

    def login(self, email=None, password='secret_password', role=None, is_superuser=True):
        if email is None:
            email = self.email
        if self.logged_user:
            self.logout()

        self.authorize(email, password)
        self.logged_user = self.get_logged_user()

    @staticmethod
    def get_logout_url():
        return ''

    def logout(self):
        self.driver.open_url(self.get_logout_url())
        self.logged_user = None

    def authorize(self, email, password):
        self.driver.open_url('/')
        self.driver.type_in('input' + getattr(config, 'USERNAME'), email)
        self.driver.type_in('input' + getattr(config, 'PASSWORD'), password)
        self.driver.click(getattr(config, 'BTN_SUBMIT'))

    def css(self, selector):
        return self.driver.find(selector)

    def css_in(self, selector):
        return self.css(' '.join((self.main_wrapper, selector)))

    def css_in_type(self, selector, text):
        self.type_into(self.css_in(selector), text)

    def css_type(self, selector, text):
        self.type_into(self.css(selector), text)

    def type_into(self, el, text):
        el.clear()
        el.send_keys(text)

    def save(self):
        self.css(getattr(config, 'BTN_SAVE')).click()

    def save_and_continue(self):
        self.css(getattr(config, 'BTN_SAVE_AND_CONTINUE')).click()

    def cancel(self):
        self.css(getattr(config, 'BTN_CANCEL')).click()

    def drag_and_drop(self, source, target):
        return ActionChains(self.driver).drag_and_drop(source, target)

    def css_attr(self, selector, attr):
        return self.css(selector).get_attribute(attr)

    def close_flash(self, type):
        selector = ''.join((getattr(config, 'FLASH'), type, ' ', getattr(config, 'FLASH_ICON_CLOSE')))
        self.driver.wait_element_present(selector)
        self.css(selector).click()

    def save_modal_form(self):
        self.css('.modal-dialog .btn-save').click()

    def _get_element_from_selector(self, selector_or_el):
        if isinstance(selector_or_el, str):
            selector_or_el = self.css(selector_or_el)
        return selector_or_el
