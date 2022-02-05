import os
import sys
import uuid


def _python_version_at_least(required_major, required_minor, required_micro=0):
    major, minor, micro, releaselevel, serial = sys.version_info
    return (
        (major >= required_major)
        and (minor >= required_minor)
        and (micro >= required_micro)
    )


if _python_version_at_least(3, 10, 0):
    # NoseTests is not compatible with Python versions >= 3.10
    TEST_RUNNER = "django.test.runner.DiscoverRunner"
else:
    # Pretty print test results with NoseTests
    TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

NOSE_ARGS = [
    "--with-spec",
    "--spec-color",
    "--logging-clear-handlers",
    "--traverse-namespace",  # Required since Python 3.8
    "--exe",
]

# Randomise domain name at test runtime.
DOMAIN_NAME = f"example-url-{uuid.uuid4().hex[::5]}.org"
ALLOWED_HOSTS = [
    DOMAIN_NAME,
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "some-test-key"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.flatpages",
    "django.contrib.sites",
    # Apps for django-wm
    "mentions",
    "tests",
]

MIDDLEWARE = [
    # Middleware for django-wm
    "mentions.middleware.WebmentionHeadMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "django-wm-test.sqlite3"),
    }
}

ROOT_URLCONF = "tests.config.test_urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

WEBMENTIONS_USE_CELERY = True
WEBMENTIONS_AUTO_APPROVE = True
