"""A management command to reprocess an existing Webmention."""
import logging
from argparse import ArgumentParser
from typing import List

from django.core.management import BaseCommand

from mentions.models import Webmention
from mentions.tasks.incoming.reverify import reverify_mention

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "filters",
            nargs="+",
            help="Space-separated list of field=value queryset filters.",
        )

    def handle(self, *args, filters: List[str], **options):
        query = {}

        for filter_str in filters:
            filter_, value = filter_str.split("=")
            query[filter_] = value

        target_mentions = Webmention.objects.filter(**query)

        changed = []

        for mention in target_mentions:
            if reverify_mention(mention):
                changed.append(mention)

        log.info(f"Updated {len(changed)} mention(s):")
        for mention in changed:
            log.info(f"- {mention}")
