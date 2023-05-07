import os
import uuid

TEST_RUNNER = "tests.config.runner.PytestRunner"


def _any_str() -> str:
    return uuid.uuid4().hex[::5]


# Randomise domain name at test runtime.
DOMAIN_NAME = f"example-url-{_any_str()}.org"
ALLOWED_HOSTS = [
    DOMAIN_NAME,
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE_ID = 1
SECRET_KEY = _any_str()
ROOT_URLCONF = "tests.config.urls"
USE_TZ = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    # Apps for django-wm
    "mentions",
    "tests.test_app",
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
    }
}

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
                "mentions.context_processors.unread_webmentions",
            ],
        },
    },
]


def _log_handler(level="DEBUG"):
    return {
        "handlers": ["console"],
        "level": level,
    }


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
        "django": _log_handler("WARNING"),
        "mentions": _log_handler(),
        "tests": _log_handler(),
        "wagtail": _log_handler(),
        "wagtail.core": _log_handler(),
    },
}

WEBMENTIONS_USE_CELERY = True
WEBMENTIONS_AUTO_APPROVE = True
