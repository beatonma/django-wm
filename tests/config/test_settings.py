import os
import uuid

TEST_RUNNER = "tests.config.runner.PytestRunner"


# Randomise domain name at test runtime.
DOMAIN_NAME = f"example-url-{uuid.uuid4().hex[::5]}.org"
ALLOWED_HOSTS = [
    DOMAIN_NAME,
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "some-test-key"
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    # Apps for django-wm
    "mentions",
    "tests",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        }
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
        },
        "mentions": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

WEBMENTIONS_USE_CELERY = True
WEBMENTIONS_AUTO_APPROVE = True
