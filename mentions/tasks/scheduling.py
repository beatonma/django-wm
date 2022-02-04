import logging

from django.http import QueryDict

from mentions import options
from mentions.models.pending import PendingIncomingWebmention, PendingOutgoingContent
from mentions.tasks import process_incoming_webmention, process_outgoing_webmentions

log = logging.getLogger(__name__)


def handle_incoming_webmention(http_post: QueryDict, sent_by: str) -> None:
    """Delegate processing to `celery` if available, otherwise store for later.

    If settings.WEBMENTIONS_USE_CELERY is False, create a PendingIncomingWebmention.
    This needs to be processed at some point by running `manage.py pending_mentions`.
    """
    source = http_post["source"]
    target = http_post["target"]

    use_celery = options.use_celery()

    if use_celery:
        process_incoming_webmention.delay(
            source_url=source, target_url=target, sent_by=sent_by
        )

    else:
        PendingIncomingWebmention.objects.create(
            source_url=source, target_url=target, sent_by=sent_by
        )


def handle_outgoing_webmentions(absolute_url: str, text: str) -> None:
    """Delegate processing to `celery` if available, otherwise store for later.

    If settings.WEBMENTIONS_USE_CELERY is False, create a PendingOutgoingContent.
    This needs to be processed at some point by running `manage.py pending_mentions`.
    """
    use_celery = options.use_celery()

    if use_celery:
        process_outgoing_webmentions.delay(absolute_url, text)

    else:
        PendingOutgoingContent.objects.create(
            absolute_url=absolute_url,
            text=text,
        )


def handle_pending_webmentions(incoming: bool = True, outgoing: bool = True):
    """Synchronously process any PendingIncomingWebmention or PendingOutgoingContent instances.

    Typically run via `manage.py pending_mentions`"""

    if incoming:
        for wm in PendingIncomingWebmention.objects.all():
            log.info(f"Processing webmention from {wm.source_url})")
            process_incoming_webmention(wm.source_url, wm.target_url, wm.sent_by)
            wm.delete()

    if outgoing:
        for wm in PendingOutgoingContent.objects.all():
            log.info(f"Processing outgoing webmentions for content {wm.absolute_url}")
            process_outgoing_webmentions(wm.absolute_url, wm.text)
            wm.delete()
