import logging

from django.conf import settings

__all__ = [
    "auto_approve",
    "dashboard_public",
    "domain_name",
    "get_config",
    "max_retries",
    "retry_interval",
    "target_requires_model",
    "timeout",
    "url_scheme",
    "use_celery",
]


NAMESPACE = "WEBMENTIONS"
SETTING_USE_CELERY = f"{NAMESPACE}_USE_CELERY"
SETTING_AUTO_APPROVE = f"{NAMESPACE}_AUTO_APPROVE"
SETTING_URL_SCHEME = f"{NAMESPACE}_URL_SCHEME"
SETTING_TIMEOUT = f"{NAMESPACE}_TIMEOUT"
SETTING_MAX_RETRIES = f"{NAMESPACE}_MAX_RETRIES"
SETTING_RETRY_INTERVAL = f"{NAMESPACE}_RETRY_INTERVAL"
SETTING_DASHBOARD_PUBLIC = f"{NAMESPACE}_DASHBOARD_PUBLIC"
SETTING_INCOMING_TARGET_MODEL_REQUIRED = f"{NAMESPACE}_INCOMING_TARGET_MODEL_REQUIRED"
SETTING_ALLOW_SELF_MENTIONS = f"{NAMESPACE}_ALLOW_SELF_MENTIONS"

"""settings.DOMAIN_NAME is sometimes used by other libraries for the same purpose,
no need to lock it to our namespace."""
SETTING_DOMAIN_NAME = "DOMAIN_NAME"

DEFAULTS = {
    SETTING_DOMAIN_NAME: None,
    SETTING_AUTO_APPROVE: False,
    SETTING_URL_SCHEME: "https",
    SETTING_USE_CELERY: True,
    SETTING_TIMEOUT: 10,
    SETTING_MAX_RETRIES: 5,
    SETTING_RETRY_INTERVAL: 60 * 10,
    SETTING_DASHBOARD_PUBLIC: False,
    SETTING_INCOMING_TARGET_MODEL_REQUIRED: False,
    SETTING_ALLOW_SELF_MENTIONS: True,
}


log = logging.getLogger(__name__)


def _get_attr(key: str):
    return getattr(settings, key, DEFAULTS[key])


def get_config() -> dict:
    return {key: _get_attr(key) for key in DEFAULTS.keys()}


def domain_name() -> str:
    """Return settings.DOMAIN_NAME."""
    return _get_attr(SETTING_DOMAIN_NAME)


def use_celery() -> bool:

    """Return settings.WEBMENTIONS_USE_CELERY, or True if not set.

    This setting enables/disables the use of `celery` for running tasks.
    If disabled, user must run these tasks using `manage.py pending_mentions` management command."""
    return _get_attr(SETTING_USE_CELERY)


def auto_approve() -> bool:
    """Return settings.WEBMENTIONS_AUTO_APPROVE, or False if not set.

    If True, any received Webmentions will immediately become 'public': they will be included in `/get` API responses.
    If False, received Webmentions must be approved by a user with `approve_webmention` permissions.
    """
    return _get_attr(SETTING_AUTO_APPROVE)


def timeout() -> float:
    """Return settings.WEBMENTIONS_TIMEOUT.

    Timeout (in seconds) used for network requests when sending or verifying webmentions."""
    return _get_attr(SETTING_TIMEOUT)


def max_retries() -> int:
    """Return settings.WEBMENTIONS_MAX_RETRIES.

    We may retry processing of webmentions if the remote server is inaccessible.
    This specifies the maximum number of retries before we give up."""
    return _get_attr(SETTING_MAX_RETRIES)


def retry_interval() -> int:
    """Return settings.WEBMENTIONS_RETRY_INTERVAL.

    We may retry processing of webmentions if the remote server is inaccessible.
    This specifies the delay (in seconds) between attempts.

    If using `celery`, this should be precise. Otherwise, this will be treated
    as a minimum interval (and will also depend on `cron` or whatever you are
    using to schedule mention processing).

    Warning: If using RabbitMQ, it may need to be reconfigured if you want to
    specify an interval of more than 15 minutes. See
    https://docs.celeryq.dev/en/stable/userguide/calling.html#eta-and-countdown
    for more information."""
    return _get_attr(SETTING_RETRY_INTERVAL)


def target_requires_model() -> bool:
    """Return settings.WEBMENTIONS_INCOMING_TARGET_MODEL_REQUIRED.

    If True, incoming webmentions will only be accepted if they target a path
    that resolves to a `MentionableMixin` instance.

    If False, any target path can receive webmentions."""
    return _get_attr(SETTING_INCOMING_TARGET_MODEL_REQUIRED)


def allow_self_mentions() -> bool:
    """Return settings.WEBMENTIONS_ALLOW_SELF_MENTIONS.

    If True, you can send webmentions to yourself.
    If False, outgoing links that target your own domain name will be ignored.
    """
    return _get_attr(SETTING_ALLOW_SELF_MENTIONS)


def url_scheme() -> str:
    """Return settings.WEBMENTIONS_URL_SCHEME.

    This defaults to `https` which is hopefully what your server is using.
    It's handy to be able to choose when debugging stuff though."""
    scheme = _get_attr(SETTING_URL_SCHEME)
    if not settings.DEBUG and scheme != "https":
        log.warning(
            f"settings.{SETTING_URL_SCHEME} should not be `http` when in production!"
        )

    return scheme


def base_url() -> str:
    """For convenience, returns the combination of `url_scheme()` and `domain_name()`."""
    return f"{url_scheme()}://{domain_name()}"


def dashboard_public() -> bool:
    """Return settings.WEBMENTIONS_DASHBOARD_PUBLIC.

    This is intended to help with debugging while developing the `django-wm`
    library and probably should not be used otherwise."""
    is_dashboard_public = _get_attr(SETTING_DASHBOARD_PUBLIC)
    if not settings.DEBUG and is_dashboard_public:
        log.warning(
            f"settings.{SETTING_DASHBOARD_PUBLIC} should not be `True` when in production!"
        )

    return is_dashboard_public
