from django.conf import settings


def use_celery() -> bool:
    """Return settings.WEBMENTIONS_USE_CELERY, or True if not set.

    This setting enables/disables the use of `celery` for running tasks.
    If disabled, user must run these tasks using `manage.py pending_mentions` management command."""
    return getattr(settings, "WEBMENTIONS_USE_CELERY", True)


def auto_approve() -> bool:
    """Return settings.WEBMENTIONS_AUTO_APPROVE, or False if not set.

    If True, any received Webmentions will immediately become 'public':they will be included in `/get` API responses.
    If False, received Webmentions must be approved by a user with `approve_webmention` permissions.
    """

    if hasattr(settings, "WEBMENTIONS_AUTO_APPROVE"):
        return settings.WEBMENTIONS_AUTO_APPROVE
    return False
