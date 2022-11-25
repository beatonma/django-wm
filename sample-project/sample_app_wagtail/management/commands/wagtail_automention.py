import logging
import random

from django.conf import settings
from django.core.management import BaseCommand
from sample_app.tasks import automention as sample_app_automention
from sample_app_wagtail.tasks import automention as wagtail_automention

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not settings.AUTOMENTION_EMABLED:
            return

        if random.random() > 0.25:
            return

        if random.random() > 0.7:
            wagtail_automention()
        else:
            sample_app_automention()
