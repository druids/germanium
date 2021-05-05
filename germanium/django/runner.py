from django.test.runner import DiscoverRunner

from .utils import setup_databases


class GermaniumRunnerMixin:

    def __init__(self, **kwargs):
        self.refreshdb = kwargs.pop('refreshdb', False)
        super().__init__(**kwargs)

    def setup_databases(self, **kwargs):
        return setup_databases(
            self.verbosity, self.interactive, self.keepdb and not self.refreshdb, self.debug_sql,
            self.parallel, **kwargs
        )

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--refreshdb', action='store_true',
            help='Tells Django to refresh test database even if keepdb is turned on.',
        )


class GermaniumDiscoverRunner(GermaniumRunnerMixin, DiscoverRunner):
    pass
