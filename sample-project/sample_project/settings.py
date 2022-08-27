import os

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
DEFAULT_MENTION_TARGET = os.environ.get("DEFAULT_MENTION_TARGET") or ""
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")

try:
    import celery

    WEBMENTIONS_USE_CELERY = True
except ImportError:
    WEBMENTIONS_USE_CELERY = False

WEBMENTIONS_URL_SCHEME = "http"
WEBMENTIONS_AUTO_APPROVE = True
WEBMENTIONS_TIMEOUT = 3
WEBMENTIONS_DASHBOARD_PUBLIC = True
WEBMENTIONS_RETRY_INTERVAL = 2 * 60
WEBMENTIONS_MAX_RETRIES = 5


STATIC_URL = "/static/"
STATIC_ROOT = "/var/www/static/"

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
    "sample_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "mentions.middleware.WebmentionHeadMiddleware",
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
            "level": "INFO",
        },
        "mentions": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "sample_app": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "celery": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "celery.task": {
            "handlers": ["console"],
            "level": "DEBUG",
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
