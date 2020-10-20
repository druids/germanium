from io import StringIO

from django.core.management import call_command


def test_call_command(command, *args,  **kwargs):
    stdout_output = StringIO()
    stderr_output = StringIO()
    call_command(command, stdout=stdout_output, stderr=stderr_output, *args, **kwargs)
    return stdout_output, stderr_output
