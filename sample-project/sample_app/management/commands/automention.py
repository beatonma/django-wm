import logging
import random

from django.core.management import BaseCommand
from sample_app.tasks import automention

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        if random.random() > 0.25:
            return

        automention()
