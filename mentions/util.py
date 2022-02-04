import logging
from typing import Tuple
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


def split_url(target_url: str) -> Tuple[str, str, str]:
    scheme, full_domain, path, _, _ = urlsplit(target_url)
    domain = full_domain.split(":")[0]  # Remove port number if present
    return scheme, domain, path


def html_parser(content) -> BeautifulSoup:
    return BeautifulSoup(content, features="html5lib")


def noop_shared_task(func, *args, **kwargs):
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
