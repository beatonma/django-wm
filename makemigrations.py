"""Generate migrations for mentions app without installing it in a project."""

import sys
from importlib.util import find_spec

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

if __name__ == "__main__":
    settings.configure(**MIGRATION_SETTINGS)
    django.setup()

    args = sys.argv + ["makemigrations", "mentions"]
    execute_from_command_line(args)
