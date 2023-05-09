import random

from .app_settings import *
from .mentions_settings import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WSGI_APPLICATION = "sample_project.wsgi.application"
ROOT_URLCONF = "sample_project.urls"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SECRET_KEY = "not-very-secret"
DEBUG = True

DOMAIN_NAME = os.environ.get("DOMAIN_NAME") or "localhost"
ALLOWED_HOSTS = [
    DOMAIN_NAME,
    "localhost",
]
CSRF_TRUSTED_ORIGINS = [
    f"http://{DOMAIN_NAME}",
]

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
LOGIN_URL = "admin:login"
STATIC_URL = "/static/"
STATIC_ROOT = "/var/www/static/"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static/"),)


db = os.environ.get("POSTGRES_DB")
if db:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.environ.get("POSTGRES_DB"),
            "USER": os.environ.get("POSTGRES_USER"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
            "HOST": os.environ.get("DB_HOST"),
            "PORT": 5432,
        }
    }
else:
    _db_name = "devdb.sqlite3"
    print(f"Environment variable POSTGRES_DB is not set! Using {_db_name} instead.")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": _db_name,
        }
    }


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "mentions",
    "issues_app",
    "sample_app",
]

try:
    import wagtail

    INSTALLED_APPS += [
        "wagtail.contrib.forms",
        "wagtail.contrib.redirects",
        "wagtail.contrib.routable_page",
        "wagtail.embeds",
        "wagtail.sites",
        "wagtail.users",
        "wagtail.snippets",
        "wagtail.documents",
        "wagtail.images",
        "wagtail.search",
        "wagtail.admin",
        "wagtail",
        "modelcluster",
        "taggit",
        "sample_app_wagtail",
    ]
    WAGTAIL_SITE_NAME = "sample_app_wagtail"
    WAGTAILADMIN_BASE_URL = f"http://{DOMAIN_NAME}"
except ImportError:
    pass


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "mentions.middleware.WebmentionHeadMiddleware",
]


def _logger(level: str = "DEBUG"):
    return {"handlers": ["console"], "level": level}


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
        "django": _logger("INFO"),
        **{
            app_name: _logger()
            for app_name in [
                "mentions",
                "sample_app",
                "sample_wagtail_app",
                "issues_app",
                "celery",
                "celery.task",
            ]
        },
    },
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
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# Internationalisation
USE_TZ = True
USE_I18N = True  # Translation
USE_L10N = True  # Localised date formatting
languages = ["en-gb", "en-us", "fr-fr", "de-de"]
LANGUAGE_CODE = random.choice(languages)
