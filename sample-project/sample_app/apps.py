import logging
import sys

from django.apps import AppConfig

log = logging.getLogger(__name__)


class SampleAppConfig(AppConfig):
    name = "sample_app"

    def ready(self):
        from mentions import __version__ as mentions_version

        log.info(f"django-wm=={mentions_version}")

        if "runserver" not in sys.argv:
            # Don't create default article when running tests or migrations.
            return

        from sample_app.tasks import create_initial_article

        create_initial_article()
