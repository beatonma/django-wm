# Settings for django-wm
try:
    import celery

    # Enable celery depending on current docker configuration.
    WEBMENTIONS_USE_CELERY = True
except ImportError:
    WEBMENTIONS_USE_CELERY = False

WEBMENTIONS_URL_SCHEME = "http"
WEBMENTIONS_AUTO_APPROVE = True
WEBMENTIONS_TIMEOUT = 3
WEBMENTIONS_DASHBOARD_PUBLIC = True
WEBMENTIONS_RETRY_INTERVAL = 2 * 60
WEBMENTIONS_MAX_RETRIES = 5
# End of settings for django-wm
