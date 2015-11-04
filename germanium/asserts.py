from __future__ import unicode_literals

from germanium import config
from germanium.sugar import CSSMixin


class AssertMixin(object):

    def assert_true(self, expr, msg=None):
        self.assertTrue(expr, msg)

    def assert_false(self, expr, msg=None):
        self.assertFalse(expr, msg)

    def assert_equal(self, first, second, msg=None):
        self.assertEqual(first, second, msg)

    def assert_equals(self, first, second, msg=None):
        self.assertEquals(first, second, msg)

    def assert_not_equal(self, first, second, msg=None):
        self.assertNotEqual(first, second, msg)

    def assert_is(self, first, second, msg=None):
        self.assertIs(first, second, msg)

    def assert_is_not(self, first, second, msg=None):
        self.assertIsNot(first, second, msg)

    def assert_in(self, first, second, msg=None):
        self.assertIn(first, second, msg)

    def assert_not_in(self, first, second, msg=None):
        self.assertNotIn(first, second, msg)

    def assert_is_instance(self, obj, cls, msg=None):
        self.assertIsInstance(obj, cls, msg)

    def assert_not_instance(self, obj, cls, msg=None):
        self.assertNotInstance(obj, cls, msg)


class GermaniumAssertMixin(AssertMixin, CSSMixin):

    def assert_present(self, selector, msg=None):
        if not msg:
            msg = 'Element %s is not present' % str(selector)
        return self.assert_true(self.wait_element_present(selector), msg)

    def assert_not_present(self, selector, msg=None):
        if not msg:
            msg = 'Element %s is present' % str(selector)
        return self.assert_true(self.wait_element_present(selector, False), msg)

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
        self.assert_true(self.wait_for_visible(selector), 'Element %s is not visible' % str(selector))

    def assert_not_visible(self, selector):
        self.assert_true(self.wait_for_visible(selector, False))

    def assert_text(self, selector, text):
        # Standard element.text has problem with html inside element
        html = self.css(selector).get_attribute("innerHTML")
        texts = selector, text, html
        self.assert_true(text in html, "Text does not match.\nSelector: %s\nExpected: %s\nActual: %s\n" % texts)

    def assert_dialog_present(self):
        self.assert_present(config.MODAL_DIALOG)

    def assert_current_path(self, path, msg=None):
        splitted_url = self.driver.current_url.split('/', 3)
        current_path = ''
        if len(splitted_url) == 4:
            current_path = '/' + splitted_url[3].split('?')[0].split('#')[0]

        self.assert_equal(path, current_path, msg)
