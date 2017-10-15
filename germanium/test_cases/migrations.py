from django.apps import apps
from django.db.migrations.executor import MigrationExecutor
from django.db import connection
from .default import GermaniumTestCase


class MigrationTestCase(GermaniumTestCase):

    @property
    def app(self):
        return self.strip_module_suffix(apps.get_containing_app_config(type(self).__module__).name)

    def strip_module_suffix(self, module):
        return module.split('.')[-1]

    migrate_from = None
    migrate_to = None

    def setUp(self):
        super().setUp()
        assert self.migrate_from and self.migrate_to, (
            "TestCase '{}' must define migrate_from and migrate_to properties".format(type(self).__name__))
        migrate_from = [(self.app, self.migrate_from)]
        migrate_to = [(self.app, self.migrate_to)]
        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(migrate_from).apps

        # Reverse to the original migration
        executor.migrate(migrate_from)

        self.set_up_before_migration(old_apps)

        # Run the migration to test
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload.
        executor.migrate(migrate_to)

        self.apps = executor.loader.project_state(migrate_to).apps

    def set_up_before_migration(self, apps):
        pass
