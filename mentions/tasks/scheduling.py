import logging
from itertools import chain

from django.http import QueryDict

from mentions import options
from mentions.models import OutgoingWebmentionStatus
from mentions.models.pending import PendingIncomingWebmention, PendingOutgoingContent
from mentions.tasks import process_incoming_webmention, process_outgoing_webmentions
from mentions.tasks.celeryproxy import shared_task
from mentions.tasks.outgoing import try_send_webmention

log = logging.getLogger(__name__)


__all__ = [
    "handle_pending_webmentions",
    "handle_incoming_webmention",
    "handle_outgoing_webmentions",
]


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
        _reschedule_handle_pending_webmentions()

    else:
        PendingIncomingWebmention.objects.get_or_create(
            source_url=source,
            target_url=target,
            defaults={
                "sent_by": sent_by,
            },
        )


def handle_outgoing_webmentions(absolute_url: str, text: str) -> None:
    """Delegate processing to `celery` if available, otherwise store for later.

    If settings.WEBMENTIONS_USE_CELERY is False, create a PendingOutgoingContent.
    This needs to be processed at some point by running `manage.py pending_mentions`.
    """
    use_celery = options.use_celery()

    if use_celery:
        process_outgoing_webmentions.delay(source_urlpath=absolute_url, text=text)
        _reschedule_handle_pending_webmentions()

    else:
        PendingOutgoingContent.objects.get_or_create(
            absolute_url=absolute_url,
            defaults={
                "text": text,
            },
        )


@shared_task
def handle_pending_webmentions(incoming: bool = True, outgoing: bool = True):
    """Process any webmentions that are pending processing, including retries.

    Typically run via `manage.py pending_mentions`"""

    if incoming:
        _handle_pending_incoming()

    if outgoing:
        _handle_pending_outgoing()

    if options.use_celery():
        _reschedule_handle_pending_webmentions()


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
        # OutgoingWebmentionStatus created instead to track status of individual links.
        pending_out.delete()


def _reschedule_handle_pending_webmentions():
    # Schedule another run if there are still items awaiting retry.
    should_reschedule = (
        PendingIncomingWebmention.objects.filter(is_awaiting_retry=True).exists()
        or OutgoingWebmentionStatus.objects.filter(is_awaiting_retry=True).exists()
    )

    if not should_reschedule:
        return

    import celery

    # Check if this task is already scheduled.
    task = handle_pending_webmentions
    task_name = ".".join([task.__module__, task.__name__])

    app = celery.current_app
    scheduled = app.control.inspect().scheduled()
    scheduled_task_etas = [
        item["eta"]
        for item in chain.from_iterable(scheduled.values())
        if item["request"]["name"] == task_name
    ]

    if scheduled_task_etas:
        log.info(f"Skipping: task {task_name} eta {scheduled_task_etas}")
        return

    # Schedule fresh task
    task.apply_async(
        countdown=options.retry_interval(),
        expires=options.retry_interval() * 2,
    )
