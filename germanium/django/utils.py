from django.core.management import call_command
from django.conf import settings
from django.db import connections
from django.test.utils import get_unique_databases_and_mirrors


def setup_databases(verbosity, interactive, keepdb=False, debug_sql=False, parallel=0, aliases=None, **kwargs):
    """Create the test databases."""
    test_databases, mirrored_aliases = get_unique_databases_and_mirrors(aliases)

    old_names = []

    for db_name, aliases in test_databases.values():
        first_alias = None
        for alias in aliases:
            connection = connections[alias]
            old_names.append((connection, db_name, first_alias is None))

            # Actually create the database for the first connection
            if first_alias is None:
                first_alias = alias
                connection.creation.create_test_db(
                    verbosity=verbosity,
                    autoclobber=not interactive,
                    keepdb=keepdb,
                    serialize=connection.settings_dict['TEST'].get('SERIALIZE', True),
                )

                test_fixtures = getattr(settings, 'GERMANIUM_GLOBAL_FIXTURES', {}).get(alias, None)
                if test_fixtures:
                    call_command('loaddata', *test_fixtures, **{'verbosity': 0, 'database': alias})

                if parallel > 1:
                    for index in range(parallel):
                        connection.creation.clone_test_db(
                            suffix=str(index + 1),
                            verbosity=verbosity,
                            keepdb=keepdb,
                        )
            # Configure all other connections as mirrors of the first one
            else:
                connections[alias].creation.set_as_test_mirror(connections[first_alias].settings_dict)

    # Configure the test mirrors.
    for alias, mirror_alias in mirrored_aliases.items():
        connections[alias].creation.set_as_test_mirror(
            connections[mirror_alias].settings_dict)

    if debug_sql:
        for alias in connections:
            connections[alias].force_debug_cursor = True

    return old_names
