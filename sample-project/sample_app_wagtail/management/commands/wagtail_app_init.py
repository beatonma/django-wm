import logging

from django.core.management import BaseCommand
from sample_app_wagtail.models import BlogIndexPage
from sample_app_wagtail.tasks import create_initial_pages

from mentions import __version__ as mentions_version

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info(f"django-wm=={mentions_version}")

        if BlogIndexPage.objects.all().exists():
            return

        try:
            create_initial_pages()
        except Exception as e:
            log.error(f"create_initial_pages failed | {e}")
