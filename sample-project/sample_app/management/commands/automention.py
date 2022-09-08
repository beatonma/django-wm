import logging
import random

from django.conf import settings
from django.core.management import BaseCommand
from sample_app.models import create_article

from mentions.models.mixins import IncomingMentionType

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        if random.random() > 0.25:
            return

        url = random.choice(settings.AUTOMENTION_URLS)
        create_article(
            author="automention",
            target_url=url,
            mention_type=random.choice(list(IncomingMentionType.__members__.keys())),
        )
        log.info(f"automention: mentioned url {url}")
