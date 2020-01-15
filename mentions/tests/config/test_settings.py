import os

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-spec',
    '--spec-color',
    '--logging-clear-handlers',
    '--traverse-namespace',  # Required since Python 3.8
]

DOMAIN_NAME = 'example.org'
ALLOWED_HOSTS = [
    DOMAIN_NAME,
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'some-test-key'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.sites',

    # Apps for django-wm
    'mentions',
    'mentions.tests',
]

MIDDLEWARE = [
    # Middleware for django-wm
    'mentions.middleware.WebmentionHeadMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

ROOT_URLCONF = 'mentions.tests.config.test_urls'
