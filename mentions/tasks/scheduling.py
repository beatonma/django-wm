import logging

from django.http import QueryDict

from mentions import options
from mentions.models import OutgoingWebmentionStatus
from mentions.models.pending import PendingIncomingWebmention, PendingOutgoingContent
from mentions.tasks import process_incoming_webmention, process_outgoing_webmentions
from mentions.tasks.outgoing import try_send_webmention

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
            source_url=source,
            target_url=target,
            sent_by=sent_by,
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
        process_outgoing_webmentions.delay(source_urlpath=absolute_url, text=text)

    else:
        PendingOutgoingContent.objects.create(
            absolute_url=absolute_url,
            text=text,
        )


def handle_pending_webmentions(incoming: bool = True, outgoing: bool = True):
    """Synchronously process any PendingIncomingWebmention or PendingOutgoingContent instances.

    Typically run via `manage.py pending_mentions`"""

    if incoming:
        _handle_pending_incoming()

    if outgoing:
        _handle_pending_outgoing()


def _handle_pending_incoming():
    for incoming_wm in PendingIncomingWebmention.objects.filter(is_awaiting_retry=True):
        if incoming_wm.can_retry():
            process_incoming_webmention(
                incoming_wm.source_url,
                incoming_wm.target_url,
                incoming_wm.sent_by,
            )

            incoming_wm.refresh_from_db()
            if incoming_wm.is_retry_successful:
                # Webmention created successfully so this is no longer needed.
                incoming_wm.delete()


def _handle_pending_outgoing():
    for outgoing_retry in OutgoingWebmentionStatus.objects.filter(
        is_awaiting_retry=True,
    ):
        if outgoing_retry.can_retry():
            try_send_webmention(outgoing_retry.source_url, outgoing_retry.target_url)

    for pending_out in PendingOutgoingContent.objects.all():
        process_outgoing_webmentions(pending_out.absolute_url, pending_out.text)
        pending_out.delete()
