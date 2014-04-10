import time

from germanium import config

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException

from django_selenium.testcases import wait, SeleniumElement


class CSSMixin(object):
    main_wrapper = ''

    def css(self, selector):
        return SeleniumElement(self.driver.find_elements_by_css_selector(selector), selector)

    def css_in(self, selector):
        return self.css(' '.join((self.main_wrapper, selector)))

    def css_in_type(self, selector, text):
        self.css_type(self.css_in(selector), text)

    def type(self, selector_or_element, text):
        el = self._get_element_from_selector(selector_or_element)
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

    def css_attr(self, selector_or_element, attr):
        return self._get_element_from_selector(selector_or_element).get_attribute(attr)

    def close_flash(self, type):
        selector = ''.join((config.FLASH, type, ' ', config.FLASH_ICON_CLOSE))
        self.driver.wait_element_present(selector)
        self.css(selector).click()

    def save_modal_form(self):
        self.css(' '.join((config.MODAL_DIALOG, config.BTN_SAVE))).click()

    def _get_element_from_selector(self, selector_or_el):
        if not isinstance(selector_or_el, SeleniumElement):
            selector_or_el = self.css(selector_or_el)
        return selector_or_el

    @wait
    def wait_for_text(self, selector, text):
        return text in self.css(selector).text

    @wait
    def wait_for_visible(self, selector, visible=True):
        return self.css(selector).is_displayed() == visible

    @wait
    def wait_element_present(self, selector, present=True):
        return self.is_element_present(selector) == present

    def is_element_present(self, selector):
        return len(self.driver.find_elements_by_css_selector(selector)) > 0

    def click(self, selector_or_element):
        self._get_element_from_selector(selector_or_element).click()

    def click_and_wait(self, selector_or_element, timeout=1):
        self._get_element_from_selector(selector_or_element).click()
        time.sleep(timeout)

    def select(self, selector, val):
        self.click(selector + (' option[value="%s"]' % val))
