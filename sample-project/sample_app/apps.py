import logging
import sys

from django.apps import AppConfig

log = logging.getLogger(__name__)


class SampleAppConfig(AppConfig):
    name = "sample_app"

    def ready(self):
        if "runserver" not in sys.argv:
            # Don't create default article when running tests or migrations.
            return

        from sample_app.models import Article
        from sample_app.tasks import create_initial_articles

        from mentions import __version__ as mentions_version
        from mentions.models import OutgoingWebmentionStatus

        log.info(f"django-wm=={mentions_version}")

        if Article.objects.all().exists():
            # Run once when server is created, never again.
            return

        create_initial_articles()

        OutgoingWebmentionStatus.objects.get_or_create(
            target_url="#s3",
            source_url="/article/2/",
        )  # Invalid target url: should be deleted when handle_pending_webmentions is called.
