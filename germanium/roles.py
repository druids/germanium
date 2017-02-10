from __future__ import unicode_literals

from germanium.germanium_selenium import GermaniumTestCase


class AsSuperuserTestCase(GermaniumTestCase):

    def set_up(self):
        super(AsSuperuserTestCase, self).set_up()
        self.login(role='superuser', is_superuser=True)
