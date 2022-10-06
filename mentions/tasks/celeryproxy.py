import logging

from mentions import options

__all__ = [
    "get_logger",
    "shared_task",
]

log = logging.getLogger(__name__)


def _noop_shared_task(func, *args, **kwargs):
    """No-op replacement for @decorators that may not be available.

    If the user disables celery via `settings.WEBMENTIONS_USE_CELERY = False`,
    `celery` may not be installed. If `celery` cannot be imported then we need to
    provide an implementation so that un-importable `@shared_task` decorators
    don't break everything.
    """

    class Proxy:
        def delay(self, *args, **kwargs):
            raise NotImplementedError(
                "Called delay() on shared_task but `celery` is not installed! "
                "To disable Celery in `django-wm`, make sure "
                "settings.MENTION_USE_CELERY is False."
            )

        def __call__(self, *args, **kwargs):
            if options.use_celery():
                log.warning("Celery is not installed!")
            return func(*args, **kwargs)

    return (lambda *a, **kw: Proxy())(*args, **kwargs)


try:
    from celery import shared_task
    from celery.utils.log import get_task_logger as _get_task_logger

    get_logger = _get_task_logger

except (ImportError, ModuleNotFoundError):
    shared_task = _noop_shared_task
    get_logger = logging.getLogger
