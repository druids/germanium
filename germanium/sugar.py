import time

from germanium import config

from selenium.webdriver.common.action_chains import ActionChains


class CSSMixin:

    main_wrapper = ''

    def css_in(self, selector):
        return self.css(' '.join((self.main_wrapper, selector)))

    def css_in_type(self, selector, text):
        self.css_type(self.css_in(selector), text)

    def type(self, selector_or_element, text, clear=True):
        el = self._get_element_from_selector(selector_or_element)
        if clear:
            el.clear()
        el.send_keys(text)

    def type_with_autocomplete(self, selector_or_element, text):
        self.type(selector_or_element + ' input', text)
        time.sleep(0.5)
        self.click(selector_or_element + ' li.ac-row.active')

    def save(self, wait_for_element=None):
        self.css(config.BTN_SAVE).click()
        if wait_for_element:
            self.wait_element_present(wait_for_element)

    def save_and_continue(self, wait_for_element=None):
        self.css(config.BTN_SAVE_AND_CONTINUE).click()
        if wait_for_element:
            self.wait_element_present(wait_for_element)

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
        if isinstance(selector_or_el, str):
            selector_or_el = self.css(selector_or_el)
        return selector_or_el

    def count_elements(self, selector):
        element = self._get_element_from_selector(selector)
        return len(object.__getattribute__(element, 'elements'))

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
        element = self._get_element_from_selector(selector)
        if element.tag_name == 'input':
            self.click(selector + '[value="%s"]' % val)
        elif element.tag_name == 'select':
            self.click(selector + (' option[value="%s"]' % val))
