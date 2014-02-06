from germanium import config

class AssertMixin(object):

    def assert_true(self, expr, msg):
        self.assertTrue(expr, msg)

    def assert_false(self, expr, msg):
        self.assertTrue(expr, msg)

    def assert_equal(self, first, second, msg):
        self.assertEqual(first, second, msg)

    def assert_equals(self, first, second, msg):
        self.assertEquals(first, second, msg)


class GerundiumAssertMixin(AssertMixin):

    def assert_present(self, selector, msg=None):
        return self.assertTrue(self.driver.wait_element_present(selector), msg)

    def assert_not_present(self, selector, msg=None):
        return self.assertTrue(self.driver.wait_element_present(selector, False), msg)

    def assert_success(self, text):
        selector = ''.join((config.FLASH, config.FLASH_TYPE['success'], ' ', config.FLASH_WRAPPER))
        self.driver.wait_element_present(selector)
        self.assert_text(selector, text)

    def assert_visible_loading(self):
        selector = ''.join((config.FLASH, config.FLASH_TYPE['info'], ' ', config.FLASH_WRAPPER))
        self.driver.wait_element_present(selector)
        self.assert_text(selector, 'Loading...')

    def assert_visible(self, selector):
        self.assertTrue(self.driver.wait_for_visible(selector), 'Element %s is not visible' % str(selector))

    def assert_not_visible(self, selector):
        self.assertTrue(self.driver.wait_for_visible(selector, False))

    def assert_text(self, selector, text):
        # Standard element.text has problem with html inside element
        html = self.css(selector).get_attribute("innerHTML")
        texts = selector, text, html
        self.assertTrue(text in html, "Text does not match.\nSelector: %s\nExpected: %s\nActual: %s\n" % texts)

    def assert_dialog_present(self):
        self.assert_present(config.MODAL_DIALOG)
