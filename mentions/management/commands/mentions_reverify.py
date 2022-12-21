"""A management command to reprocess an existing Webmention."""
import logging
from argparse import ArgumentParser
from typing import List

from django.core.management import BaseCommand
from django.db.models import QuerySet

from mentions.models import Webmention
from mentions.tasks.incoming.reverify import reverify_mention

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "filters",
            nargs="*",
            help="Space-separated list of field=value queryset filters.",
        )

        parser.add_argument(
            "--all",
            dest="all_mentions",
            action="store_true",
            default=False,
            help="Reverify all webmentions.",
        )

    def handle(self, *args, filters: List[str], all_mentions: bool, **options):
        target_mentions = get_target_mentions(filters, all_mentions)

        changed = []

        for mention in target_mentions:
            if reverify_mention(mention):
                changed.append(mention)

        log.info(f"Updated {len(changed)} mention(s):")
        for mention in changed:
            log.info(f"- {mention}")


def get_target_mentions(filters: List[str], all_mentions: bool) -> QuerySet[Webmention]:
    if all_mentions:
        return Webmention.objects.all()

    if not filters:
        raise ValueError(
            "Please provide at least one field=value queryset filter. "
            "To reverify all Webmentions, use --all to explicitly bypass filtering."
        )

    query = {}
    for filter_str in filters:
        filter_, value = filter_str.split("=")
        query[filter_] = value

    return Webmention.objects.filter(**query)
