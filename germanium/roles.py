from germanium import GermaniumTestCase


class AsSuperuserTestCase(GermaniumTestCase):

    def setUp(self):
        super(AsSuperuserTestCase, self).setUp()
        self.login(role='superuser', is_superuser=True)


class AsReadOnlyUserTestCase(GermaniumTestCase):

    def setUp(self):
        super(AsReadOnlyUserTestCase, self).setUp()
        self.login(role='readonly', is_superuser=False)
