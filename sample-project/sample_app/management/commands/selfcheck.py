import logging
import time

import requests
from django.conf import settings
from django.core.management import BaseCommand

import mentions

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        self_check()


def self_check():
    time.sleep(5)
    failed = False
    log.info(f"django-wm=={mentions.__version__} self-check:")
    for urlpath in [
        "/article/1/",
        "/webmention/",
        "/webmention/get?url=/article/1/",
        "/webmention/dashboard/",
    ]:
        url = f"http://{settings.DOMAIN_NAME}{urlpath}"
        r = requests.get(url, timeout=2)

        if r.status_code != 200:
            log.error(f"[FAIL]: {url} | {r}")
            failed = True

        log.info(f"[OK] {urlpath}")

    if failed:
        raise Exception("Self-check failed")

    log.info(f"[OK] django-wm=={mentions.__version__} self-check complete!")
