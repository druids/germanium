from germanium.germanium_selenium import GermaniumTestCase


class AsSuperuserTestCase(GermaniumTestCase):

    def setUp(self):
        super(AsSuperuserTestCase, self).setUp()
        self.login(role='superuser', is_superuser=True)
