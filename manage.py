"""Generate migrations for mentions app without installing it in a project."""
import argparse
import sys
from importlib.util import find_spec
from typing import List, Tuple

import django
from django.conf import settings
from django.core.management import execute_from_command_line

extra_apps = []
is_wagtail_installed = find_spec("wagtail") is not None
if is_wagtail_installed:
    extra_apps += ["wagtail"]

MIGRATION_SETTINGS = {
    "DEBUG": False,
    "SECRET_KEY": "django-wm-fake-key",
    "INSTALLED_APPS": [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "mentions",
        *extra_apps,
    ],
    "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
}


def parse_args() -> Tuple[argparse.Namespace, List[str]]:
    parser = argparse.ArgumentParser()

    subs = parser.add_subparsers(dest="command")
    subs.add_parser("makemigrations")

    return parser.parse_known_args()


if __name__ == "__main__":
    program = [sys.argv[0]]
    args_, remaining = parse_args()
    sys.argv = program + remaining

    settings.configure(**MIGRATION_SETTINGS)
    django.setup()

    args = sys.argv + [args_.command]

    execute_from_command_line(args)
