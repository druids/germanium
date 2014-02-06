import config


class Assert(object):

    def assert_present(self, selector, msg=None):
        return self.assertTrue(self.driver.wait_element_present(selector), msg)

    def assert_not_present(self, selector, msg=None):
        return self.assertTrue(self.driver.wait_element_present(selector, False), msg)

    def assert_success(self, text):
        selector = ''.join((getattr(config, 'FLASH'), getattr(config, 'FLASH_TYPE')['success'], ' ', getattr(config, 'FLASH_WRAPPER')))
        self.driver.wait_element_present(selector)
        self.assert_text(selector, text)

    def assert_visible_loading(self):
        selector = ''.join((getattr(config, 'FLASH'), getattr(config, 'FLASH_TYPE')['info'], ' ', getattr(config, 'FLASH_WRAPPER')))
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
        self.assert_present(getattr(config, 'MODAL_DIALOG'))
