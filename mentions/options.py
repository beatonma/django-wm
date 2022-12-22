"""Options for `django-wm` are configured by adding attributes to Django settings.

These may be defined in either of the following two formats. Choose one format
or the other. If `WEBMENTIONS` is defined, the latter format will be ignored.

# settings.py
WEBMENTIONS = {
    "TIMEOUT": 10,
    "USE_CELERY": True,
}

--- or ---

# settings.py
WEBMENTIONS_TIMEOUT = 10
WEBMENTIONS_USE_CELERY = True

"""

import logging
from typing import Dict

from django.conf import settings

import mentions

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
    "user_agent",
]


NAMESPACE = "WEBMENTIONS"
SETTING_ALLOW_OUTGOING_DEFAULT = f"{NAMESPACE}_ALLOW_OUTGOING_DEFAULT"
SETTING_ALLOW_SELF_MENTIONS = f"{NAMESPACE}_ALLOW_SELF_MENTIONS"
SETTING_AUTO_APPROVE = f"{NAMESPACE}_AUTO_APPROVE"
SETTING_DASHBOARD_PUBLIC = f"{NAMESPACE}_DASHBOARD_PUBLIC"
SETTING_DEFAULT_URL_PARAMETER_MAPPING = f"{NAMESPACE}_DEFAULT_URL_PARAMETER_MAPPING"
SETTING_INCOMING_TARGET_MODEL_REQUIRED = f"{NAMESPACE}_INCOMING_TARGET_MODEL_REQUIRED"
SETTING_MAX_RETRIES = f"{NAMESPACE}_MAX_RETRIES"
SETTING_RETRY_INTERVAL = f"{NAMESPACE}_RETRY_INTERVAL"
SETTING_TIMEOUT = f"{NAMESPACE}_TIMEOUT"
SETTING_URL_SCHEME = f"{NAMESPACE}_URL_SCHEME"
SETTING_USE_CELERY = f"{NAMESPACE}_USE_CELERY"
SETTING_USER_AGENT = f"{NAMESPACE}_USER_AGENT"

"""settings.DOMAIN_NAME is sometimes used by other libraries for the same purpose,
no need to lock it to our namespace."""
SETTING_DOMAIN_NAME = "DOMAIN_NAME"

DEFAULTS = {
    SETTING_ALLOW_OUTGOING_DEFAULT: False,
    SETTING_ALLOW_SELF_MENTIONS: True,
    SETTING_AUTO_APPROVE: False,
    SETTING_DASHBOARD_PUBLIC: False,
    SETTING_DEFAULT_URL_PARAMETER_MAPPING: {"object_id": "id"},
    SETTING_DOMAIN_NAME: None,
    SETTING_INCOMING_TARGET_MODEL_REQUIRED: False,
    SETTING_MAX_RETRIES: 5,
    SETTING_RETRY_INTERVAL: 60 * 10,
    SETTING_TIMEOUT: 10,
    SETTING_URL_SCHEME: "https",
    SETTING_USE_CELERY: True,
    SETTING_USER_AGENT: f"django-wm/{mentions.__version__} (+{mentions.__url__})",
}


log = logging.getLogger(__name__)


def _get_attr(key: str):
    if not key.startswith(NAMESPACE) or not hasattr(settings, NAMESPACE):
        return getattr(settings, key, DEFAULTS[key])

    opts: dict = getattr(settings, NAMESPACE)
    simple_key = key[len(f"{NAMESPACE}_") :]
    return opts.get(simple_key, DEFAULTS[key])


def get_config() -> dict:
    return {key: _get_attr(key) for key in DEFAULTS.keys()}


def allow_outgoing_default() -> bool:
    """Return settings.WEBMENTIONS_ALLOW_OUTGOING_DEFAULT.

    Sets the default value for `MentionableMixin.allow_outgoing_webmentions`."""

    return _get_attr(SETTING_ALLOW_OUTGOING_DEFAULT)


def allow_self_mentions() -> bool:
    """Return settings.WEBMENTIONS_ALLOW_SELF_MENTIONS.

    If True, you can send webmentions to yourself.
    If False, outgoing links that target your own domain name will be ignored.
    """
    return _get_attr(SETTING_ALLOW_SELF_MENTIONS)


def auto_approve() -> bool:
    """Return settings.WEBMENTIONS_AUTO_APPROVE, or False if not set.

    If True, any received Webmentions will immediately become 'public': they will be included in `/get` API responses.
    If False, received Webmentions must be approved by a user with `approve_webmention` permissions.
    """
    return _get_attr(SETTING_AUTO_APPROVE)


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


def default_url_parameter_mapping() -> Dict[str, str]:
    """Return settings.WEBMENTIONS_DEFAULT_URL_PARAMETER_MAPPING.

    This is used by `MentionableMixin.resolve_from_url_kwargs` if you do not
    override it on your model.

    The first value is the name of the parameter captured from your URL pattern,
    the second is the name of the field on the model.

    e.g. The default {"object_id": "id"} will result in a model query that looks
    like `MyModel.objects.get(id=url_kwargs.get("object_id"))`.
    """
    return _get_attr(SETTING_DEFAULT_URL_PARAMETER_MAPPING)


def domain_name() -> str:
    """Return settings.DOMAIN_NAME."""
    return _get_attr(SETTING_DOMAIN_NAME)


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


def timeout() -> float:
    """Return settings.WEBMENTIONS_TIMEOUT.

    Timeout (in seconds) used for network requests when sending or verifying webmentions."""
    return _get_attr(SETTING_TIMEOUT)


def url_scheme() -> str:
    """Return settings.WEBMENTIONS_URL_SCHEME.

    This defaults to `https` which is hopefully what your server is using.
    It's handy to be able to choose when debugging stuff though."""
    return _get_attr(SETTING_URL_SCHEME)


def use_celery() -> bool:
    """Return settings.WEBMENTIONS_USE_CELERY, or True if not set.

    This setting enables/disables the use of `celery` for running tasks.
    If disabled, user must run these tasks using `manage.py pending_mentions` management command."""
    return _get_attr(SETTING_USE_CELERY)


def user_agent() -> str:
    """Return settings.WEBMENTIONS_USER_AGENT.

    This is included with all network requests made by `django-wm`."""
    return _get_attr(SETTING_USER_AGENT)
