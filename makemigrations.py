"""Generate migrations for mentions app without installing it in a project."""

import sys

import django
from django.conf import settings
from django.core.management import execute_from_command_line

MIGRATION_SETTINGS = {
    "DEBUG": False,
    "SECRET_KEY": "django-wm-fake-key",
    "INSTALLED_APPS": [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "mentions",
    ],
    "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
}

if __name__ == "__main__":
    settings.configure(**MIGRATION_SETTINGS)
    django.setup()

    args = sys.argv + ["makemigrations", "mentions"]
    execute_from_command_line(args)
