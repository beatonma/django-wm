import logging

from django.conf import settings

NAMESPACE = "WEBMENTIONS"
SETTING_USE_CELERY = f"{NAMESPACE}_USE_CELERY"
SETTING_AUTO_APPROVE = f"{NAMESPACE}_AUTO_APPROVE"
SETTING_URL_SCHEME = f"{NAMESPACE}_URL_SCHEME"
SETTING_DOMAIN_NAME = "DOMAIN_NAME"

DEFAULTS = {
    SETTING_DOMAIN_NAME: None,
    SETTING_AUTO_APPROVE: False,
    SETTING_URL_SCHEME: "https",
    SETTING_USE_CELERY: True,
}


log = logging.getLogger(__name__)


def _get_attr(key: str):
    return getattr(settings, key, DEFAULTS[key])


def get_config() -> dict:
    return {key: _get_attr(key) for key in DEFAULTS.keys()}


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


def url_scheme() -> str:
    """Return settings.WEBMENTIONS_URL_SCHEME.

    This defaults to `https` which is hopefully what your server is using.
    It's handy to be able to choose when debugging stuff though."""
    scheme = _get_attr(SETTING_URL_SCHEME)
    if not settings.DEBUG and scheme == "https":
        log.warning(
            f"settings.{SETTING_URL_SCHEME} should not be `http` when in production!"
        )

    return scheme


__all__ = [
    "use_celery",
    "auto_approve",
    "url_scheme",
]
