from django.core.management import BaseCommand

from mentions.tasks.scheduling import handle_pending_webmentions

PENDING_TYPE_ALL = "all"
PENDING_TYPE_INCOMING = "incoming"
PENDING_TYPE_OUTGOING = "outgoing"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "pending_type",
            choices=[PENDING_TYPE_ALL, PENDING_TYPE_INCOMING, PENDING_TYPE_OUTGOING],
            default=PENDING_TYPE_ALL,
            nargs="?",
            help=f"Only process incoming or outgoing pending webmention content. Default: {PENDING_TYPE_ALL}",
        )

    def handle(self, pending_type, *args, **options):
        incoming = pending_type == PENDING_TYPE_INCOMING
        outgoing = pending_type == PENDING_TYPE_OUTGOING

        if pending_type == PENDING_TYPE_ALL:
            incoming = True
            outgoing = True

        self.stdout.write(f"Checking for pending webmentions [{pending_type}]...")

        handle_pending_webmentions(incoming=incoming, outgoing=outgoing)
