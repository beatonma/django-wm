#!env/bin/python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

SETTINGS_PATH = "tests.config.settings"


def _get_sys_args() -> list:
    args_ = sys.argv
    position = None
    for index, x in enumerate(args_):
        if x.endswith("runtests.py"):
            position = index + 1
            break

    return args_[position:]


if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = SETTINGS_PATH

    django.setup()

    test_runner = get_runner(settings)()

    # Detailed report for any tests that are non-passing (failed, skipped...)
    default_args = "-r a".split(" ")
    args = _get_sys_args() or default_args
    failures = test_runner.run_tests(["tests", *args])

    sys.exit(bool(failures))
