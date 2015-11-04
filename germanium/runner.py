from __future__ import unicode_literals

import sys
import unittest
import django
import nose.core

from django.test.testcases import SimpleTestCase

from django_nose.runner import NoseTestSuiteRunner, _get_plugins_from_settings
from django_nose.plugin import ResultPlugin, TestReorderer, AlwaysOnPlugin
from django_nose.utils import is_subclass_at_all


class GermaniumDjangoSetUpPlugin(AlwaysOnPlugin):
    """
    Configures Django to set up and tear down the environment

    This allows coverage to report on all code imported and used during the
    initialization of the test runner.

    Database is set-up only if it is necessary
    """
    name = 'germanium django setup'
    score = 150

    def __init__(self, runner):
        super(GermaniumDjangoSetUpPlugin, self).__init__()
        self.runner = runner
        self.sys_stdout = sys.stdout
        self.is_database_set_up = False

    def _get_test_cases(self, suite):
        if is_subclass_at_all(suite.context, unittest.TestCase):
            return [suite.context]

        test_clases = []
        if hasattr(suite, '_get_tests'):
            for test in suite._get_tests():
                test_clases += self._get_test_cases(test)
        return test_clases

    def _need_database(self, test):
        for test_case in self._get_test_cases(test):
            if issubclass(test_case, SimpleTestCase):
                return True
        return False

    def prepareTest(self, test):
        """Create the Django DB and model tables, and do other setup.

        This isn't done in begin() because that's too early--the DB has to be
        set up *after* the tests are imported so the model registry contains
        models defined in tests.py modules. Models are registered at
        declaration time by their metaclass.

        prepareTestRunner() might also have been a sane choice, except that, if
        some plugin returns something from it, none of the other ones get
        called. I'd rather not dink with scores if I don't have to.

        """
        # What is this stdout switcheroo for?
        sys_stdout = sys.stdout
        sys.stdout = self.sys_stdout

        self.runner.setup_test_environment()

        if self._need_database(test):
            self.old_names = self.runner.setup_databases()
            self.is_database_set_up = True

        sys.stdout = sys_stdout

    def finalize(self, result):
        if self.is_database_set_up:
            self.runner.teardown_databases(self.old_names)
        self.runner.teardown_test_environment()


class GermaniumNoseTestSuiteRunner(NoseTestSuiteRunner):

    def run_suite(self, nose_argv):
        result_plugin = ResultPlugin()
        plugins_to_add = [GermaniumDjangoSetUpPlugin(self), result_plugin, TestReorderer()]

        for plugin in _get_plugins_from_settings():
            plugins_to_add.append(plugin)

        try:
            django.setup()
        except AttributeError:
            # Setup isn't necessary in Django < 1.7
            pass

        nose.core.TestProgram(argv=nose_argv, exit=False,
                              addplugins=plugins_to_add)
        return result_plugin.result
