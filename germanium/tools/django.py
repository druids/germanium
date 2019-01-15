from io import StringIO

from django.core.management import call_command


def test_call_command(command, *args,  **kwargs):
    call_command(command, stdout=StringIO(), stderr=StringIO(), *args, **kwargs)
