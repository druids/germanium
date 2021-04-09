from io import StringIO

from contextlib import contextmanager

from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, connections


class OnCommitCallbacks:

    def __init__(self, connection):
        self._connection = connection
        self._start_count = len(connection.run_on_commit)
        self._end_count = None
        self.executed_callbacks = []

    def get_callbacks(self):
        if self._end_count == None:
            run_on_commit = self._connection.run_on_commit[self._start_count:]
        else:
            run_on_commit = self._connection.run_on_commit[self._start_count:self._end_count]
        return [func for sids, func in run_on_commit]

    def end(self):
        self._end_count = len(self._connection.run_on_commit)

    def execute(self):
        executed_callbacks = self.get_callbacks()
        run_on_commit_count = len(self._connection.run_on_commit)

        for callback in executed_callbacks:
            callback()
        self._connection.run_on_commit = (
            self._connection.run_on_commit[:self._start_count]
            + self._connection.run_on_commit[self._start_count + len(executed_callbacks):]
        )

        self._start_count = run_on_commit_count - len(executed_callbacks)
        self._end_count = len(self._connection.run_on_commit)

        self.executed_callbacks.append(executed_callbacks)
        return executed_callbacks

    def execute_cascade(self):
        while self.execute():
            pass


@contextmanager
def capture_on_commit_callbacks(*, using=DEFAULT_DB_ALIAS, execute=False, execute_cascade=False):
    callbacks = OnCommitCallbacks(connections[using])
    try:
        yield callbacks
    finally:
        callbacks.end()
        if execute_cascade:
            callbacks.execute_cascade()
        elif execute:
            callbacks.execute()


def test_call_command(command, *args,  **kwargs):
    execute_on_commit = kwargs.pop('execute_on_commit', False)
    execute_on_commit_cascade = kwargs.pop('execute_on_commit_cascade', False)
    with capture_on_commit_callbacks(execute=execute_on_commit, execute_cascade=execute_on_commit_cascade):
        stdout_output = StringIO()
        stderr_output = StringIO()
        call_command(command, stdout=stdout_output, stderr=stderr_output, *args, **kwargs)
    return stdout_output, stderr_output
