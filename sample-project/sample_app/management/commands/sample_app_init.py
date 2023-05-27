import logging

from django.core.management import BaseCommand
from sample_app.models import Article
from sample_app.tasks import create_initial_articles

from mentions import __version__ as mentions_version

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info(f"django-wm=={mentions_version}")

        if Article.objects.all().exists():
            # Run once when server is created, never again.
            return

        create_initial_articles()
