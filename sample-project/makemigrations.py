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
        "sample_app",
        # wagtail
        "wagtail.users",
        "wagtail",
        "sample_app_wagtail",
        "issues_app",
    ],
    "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
    "DOMAIN_NAME": "null.null",
    "DATABASES": {
        "default": {
            "ENGINE": "django.db.backends.dummy",
        }
    },
}


if __name__ == "__main__":
    settings.configure(**MIGRATION_SETTINGS)
    django.setup()

    args = sys.argv + [
        "makemigrations",
        "sample_app",
        "sample_app_wagtail",
        "issues_app",
    ]
    execute_from_command_line(args)
