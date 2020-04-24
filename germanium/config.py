from django.conf import settings


FLASH = getattr(settings, 'FLASH', '.flash')
FLASH_TYPE = getattr(settings, 'FLASH_TYPE', {
    'success': '.alert-success',
    'info': '.alert-info',
    'warning': '.alert-warn',
    'error': '.alert-danger'
})
FLASH_WRAPPER = getattr(settings, 'FLASH_WRAPPER', '.msg-text')
FLASH_ICON_CLOSE = getattr(settings, 'FLASH_ICON_CLOSE', '.goog-icon-remove')

USERNAME = getattr(settings, 'USERNAME', 'username')
PASSWORD = getattr(settings, 'PASSWORD', 'password')

BTN_SUBMIT = getattr(settings, 'BTN_SUBMIT', 'button[type="submit"]')
BTN_SAVE = getattr(settings, 'BTN_SAVE', '.btn-save')
BTN_SAVE_AND_CONTINUE = getattr(settings, 'BTN_SAVE_AND_CONTINUE', '.btn-save-and-continue')
BTN_CANCEL = getattr(settings, 'BTN_CANCEL', '.btn-cancel')

MODAL_DIALOG = getattr(settings, 'MODAL_DIALOG', '.modal-dialog')

SELENIUM_TESTS_WAIT = getattr(settings, 'SELENIUM_TESTS_WAIT', 1)
SELENIUM_DISPLAY_DIMENSION = getattr(settings, 'SELENIUM_DISPLAY_DIMENSION', (1440, 900))

SELENIUM_RUN_IN_BACKGROUND = getattr(settings, 'SELENIUM_RUN_IN_BACKGROUND', False)

LOGOUT_URL = getattr(settings, 'LOGOUT_URL', '/logout')
LOGIN_URL = getattr(settings, 'LOGIN_URL', '/login')

PHANTOM_JS_BIN = getattr(settings, 'PHANTOM_JS_BIN', 'phantomjs')
WINDOW_SIZE = (1124, 850)

TURN_OFF_MAX_DIFF = getattr(settings, 'TURN_OFF_MAX_DIFF', True)

TEST_ALL_DATABASES = getattr(settings, 'GERMANIUM_TEST_ALL_DATABASES', False)
