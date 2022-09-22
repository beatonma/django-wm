#!env/bin/python
import logging
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

log = logging.getLogger(__name__)

SETTINGS_PATH = "tests.config.test_settings"


if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = SETTINGS_PATH

    django.setup()

    test_runner = get_runner(settings)()
    failures = test_runner.run_tests(["tests"])

    sys.exit(bool(failures))
