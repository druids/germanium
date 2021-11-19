from io import StringIO

from contextlib import contextmanager

from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, connections


class CatchCallbacks:

    def __init__(self, connection, callback_name):
        self._connection = connection
        self._callback_name = callback_name
        self._start_count = len(self._watching_callbacks)
        self._end_count = None
        self._executed = False

    @property
    def _watching_callbacks(self):
        return getattr(self._connection, self._callback_name, [])

    def _set_watching_callback(self, callbacks):
        setattr(self._connection, self._callback_name, callbacks)

    def end(self):
        self._end_count = len(self._watching_callbacks)

    def get_callbacks(self, start_count=None):
        start_count = self._start_count if start_count is None else start_count

        if self._end_count == None:
            watching_callbacks = self._watching_callbacks[start_count:]
        else:
            watching_callbacks = self._watching_callbacks[start_count:self._end_count]
        return [callbacks[-1] for callbacks in watching_callbacks]

    def execute(self):
        if self._executed:
            raise RuntimeError('callback was already executed')

        executed_callbacks = []
        start_count = self._start_count
        while True:
            callbacks = self.get_callbacks(start_count)
            if not callbacks:
                break
            executed_callbacks.append(callbacks[0])
            callbacks[0]()
            start_count += 1

        if executed_callbacks:
            self._set_watching_callback(
                self._watching_callbacks[:self._start_count]
                + self._watching_callbacks[self._start_count + len(executed_callbacks):]
            )

        return executed_callbacks


class CommitCallbacks:

    def __init__(self, connection):
        self.pre_commit = CatchCallbacks(connection, 'run_pre_commit')
        self.on_commit = CatchCallbacks(connection, 'run_on_commit')

    def end(self):
        self.pre_commit.end()
        self.on_commit.end()

    def execute_pre_commit(self):
        return self.pre_commit.execute()

    def execute_on_commit(self):
        return self.on_commit.execute()

    def execute_on_commit_cascade(self):
        with capture_commit_callbacks(execute_pre_commit=True) as callbacks:
            executed_callbacks = self.execute_on_commit()

        # start count must be updated because current callback removed some values from run_on_commit list
        callbacks.on_commit._start_count -= len(executed_callbacks)
        if callbacks.on_commit.get_callbacks():
            callbacks.execute_on_commit_cascade()


@contextmanager
def capture_commit_callbacks(*, using=DEFAULT_DB_ALIAS, execute_pre_commit=False,
                             execute_on_commit=False, execute_on_commit_cascade=False):
    callbacks = CommitCallbacks(connections[using])
    try:
        yield callbacks
    finally:
        if execute_on_commit_cascade or execute_on_commit or execute_pre_commit:
            callbacks.execute_pre_commit()

        callbacks.end()

        if execute_on_commit_cascade:
            callbacks.execute_on_commit_cascade()
        elif execute_on_commit:
            callbacks.execute_on_commit()


def test_call_command(command, *args,  **kwargs):
    execute_pre_commit = kwargs.pop('execute_pre_commit', True)
    execute_on_commit = kwargs.pop('execute_on_commit', False)
    execute_on_commit_cascade = kwargs.pop('execute_on_commit_cascade', False)
    with capture_commit_callbacks(execute_pre_commit=execute_pre_commit,
                                  execute_on_commit=execute_on_commit,
                                  execute_on_commit_cascade=execute_on_commit_cascade):
        stdout_output = StringIO()
        stderr_output = StringIO()
        call_command(command, stdout=stdout_output, stderr=stderr_output, *args, **kwargs)
    return stdout_output, stderr_output
