import logging
import sys

from django.apps import AppConfig

log = logging.getLogger(__name__)


class SampleAppWagtailConfig(AppConfig):
    name = "sample_app_wagtail"

    def ready(self):
        if "runserver" not in sys.argv:
            # Don't create default article when running tests or migrations.
            return

        from sample_app_wagtail.models import BlogIndexPage
        from sample_app_wagtail.tasks import create_initial_pages

        from mentions import __version__ as mentions_version

        log.info(f"django-wm=={mentions_version}")

        if BlogIndexPage.objects.all().exists():
            return

        create_initial_pages()
