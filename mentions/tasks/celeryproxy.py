import logging

log = logging.getLogger(__name__)


def _noop_shared_task(func, *args, **kwargs):
    """No-op replacement for @decorators that may not be available.

    If the user disables celery via `settings.WEBMENTIONS_USE_CELERY = False`,
    `celery` may not be installed. If `celery` cannot be imported then we need to
    provide an implementation so that un-importable `@shared_task` decorators
    don't break everything.

    e.g:
        try:
            from celery import shared_task

        except (ImportError, ModuleNotFoundError):
            from mentions.util import noop_shared_task

            shared_task = noop_shared_task
    """

    class Proxy:
        def delay(self, *args, **kwargs):
            raise NotImplementedError(
                "Called delay() on shared_task but `celery` is not installed!"
            )

        def __call__(self, *args, **kwargs):
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
