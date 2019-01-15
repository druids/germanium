from germanium.tools import assert_true, assert_equal
from germanium import config
from germanium.sugar import CSSMixin


class GermaniumAssertMixin(CSSMixin):

    def assert_present(self, selector, msg=None):
        if not msg:
            msg = 'Element %s is not present' % str(selector)
        return assert_true(self.wait_element_present(selector), msg)

    def assert_not_present(self, selector, msg=None):
        if not msg:
            msg = 'Element %s is present' % str(selector)
        return assert_true(self.wait_element_present(selector, False), msg)

    def assert_success(self, text):
        selector = ' '.join((config.FLASH, config.FLASH_TYPE['success'], config.FLASH_WRAPPER))
        self.wait_element_present(selector)
        self.assert_text(selector, text)

    def assert_visible_success(self):
        selector = ' '.join((config.FLASH, config.FLASH_TYPE['success'], config.FLASH_WRAPPER))
        self.wait_element_present(selector)
        self.assert_visible(selector)

    def assert_visible_loading(self):
        selector = ' '.join((config.FLASH, config.FLASH_TYPE['info'], config.FLASH_WRAPPER))
        self.wait_element_present(selector)
        self.assert_text(selector, 'Loading...')

    def assert_visible(self, selector):
        assert_true(self.wait_for_visible(selector), 'Element %s is not visible' % str(selector))

    def assert_not_visible(self, selector):
        assert_true(self.wait_for_visible(selector, False))

    def assert_text(self, selector, text):
        # Standard element.text has problem with html inside element
        html = self.css(selector).get_attribute("innerHTML")
        texts = selector, text, html
        assert_true(text in html, "Text does not match.\nSelector: %s\nExpected: %s\nActual: %s\n" % texts)

    def assert_dialog_present(self):
        self.assert_present(config.MODAL_DIALOG)

    def assert_current_path(self, path, msg=None):
        splitted_url = self.driver.current_url.split('/', 3)
        current_path = ''
        if len(splitted_url) == 4:
            current_path = '/' + splitted_url[3].split('?')[0].split('#')[0]

        assert_equal(path, current_path, msg)
