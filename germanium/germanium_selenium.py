import time

from germanium import config

from django.test.testcases import LiveServerTestCase

from django_selenium.testcases import MyDriver

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains

from germanium.auth import AuthTestCaseMixin
from germanium.asserts import GermaniumAssertMixin


class ConfigurableWaitDriver(MyDriver):
    def _wait_for_page_source(self):
        try:
            page_source = self.page_source
            time.sleep(config.SELENIUM_TESTS_WAIT)
            while page_source != self.page_source:
                page_source = self.page_source
                time.sleep(config.SELENIUM_TESTS_WAIT)
            self.update_text()
        except WebDriverException:
            pass


class GermaniumTestCase(AuthTestCaseMixin, GermaniumAssertMixin, LiveServerTestCase):
    main_wrapper = ''
    logged_user = None

    @classmethod
    def setUpClass(cls):
        if config.SELENIUM_RUN_IN_BACKGROUND:
            from pyvirtualdisplay import Display
            cls.display = Display(visible=0, size=config.SELENIUM_DISPLAY_DIMENSION)
            cls.display.start()

        super(GermaniumTestCase, cls).setUpClass()

    def setUp(self):
        super(GermaniumTestCase, self).setUp()
        self.driver = ConfigurableWaitDriver()
        self.driver.set_window_size(config.SELENIUM_DISPLAY_DIMENSION[0], config.SELENIUM_DISPLAY_DIMENSION[1])
        self.driver.live_server_url = self.live_server_url

    def tearDown(self):
        time.sleep(1)
        self.driver.quit()
        super(GermaniumTestCase, self).tearDown()

    @classmethod
    def tearDownClass(cls):
        if config.SELENIUM_RUN_IN_BACKGROUND:
            cls.display.stop()
        super(GermaniumTestCase, cls).tearDownClass()

    def logout(self):
        self.driver.open_url(config.LOGOUT_URL)
        self.logged_user = None

    def authorize(self, username, password):
        self.driver.open_url('/')
        self.driver.type_in('input#id_' + config.USERNAME, username)
        self.driver.type_in('input#id_' + config.PASSWORD, password)
        self.driver.click(config.BTN_SUBMIT)

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
        self.css(config.BTN_SAVE).click()

    def save_and_continue(self):
        self.css(config.BTN_SAVE_AND_CONTINUE).click()

    def cancel(self):
        self.css(config.BTN_CANCEL).click()

    def drag_and_drop(self, source, target):
        return ActionChains(self.driver).drag_and_drop(source, target)

    def css_attr(self, selector, attr):
        return self.css(selector).get_attribute(attr)

    def close_flash(self, type):
        selector = ''.join((config.FLASH, type, ' ', config.FLASH_ICON_CLOSE))
        self.driver.wait_element_present(selector)
        self.css(selector).click()

    def save_modal_form(self):
        self.css('.modal-dialog .btn-save').click()

    def _get_element_from_selector(self, selector_or_el):
        if isinstance(selector_or_el, str):
            selector_or_el = self.css(selector_or_el)
        return selector_or_el
