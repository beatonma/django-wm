import logging
from itertools import chain

from mentions import options
from mentions.models import (
    OutgoingWebmentionStatus,
    PendingIncomingWebmention,
    PendingOutgoingContent,
)
from mentions.tasks.celeryproxy import shared_task
from mentions.tasks.incoming import process_incoming_webmention
from mentions.tasks.outgoing import (
    is_valid_target,
    process_outgoing_webmentions,
    try_send_webmention,
)

log = logging.getLogger(__name__)


__all__ = [
    "handle_pending_webmentions",
    "handle_incoming_webmention",
    "handle_outgoing_webmentions",
]


@shared_task
def handle_pending_webmentions(incoming: bool = True, outgoing: bool = True):
    """Process any webmentions that are pending processing, including retries.

    Typically run via `manage.py pending_mentions`"""

    if incoming:
        _handle_pending_incoming()

    if outgoing:
        _handle_pending_outgoing()

    if options.use_celery():
        _maybe_reschedule_handle_pending_webmentions()


def handle_incoming_webmention(source: str, target: str, sent_by: str) -> None:
    """Delegate processing to `celery` if available, otherwise store for later.

    If settings.WEBMENTIONS_USE_CELERY is False, create a PendingIncomingWebmention.
    This needs to be processed at some point by running `manage.py pending_mentions`.
    """

    use_celery = options.use_celery()

    if use_celery:
        _task_handle_incoming.delay(source, target, sent_by)

    else:
        PendingIncomingWebmention.objects.get_or_create(
            source_url=source,
            target_url=target,
            defaults={
                "sent_by": sent_by,
            },
        )


@shared_task
def _task_handle_incoming(source: str, target: str, sent_by: str):
    process_incoming_webmention(
        source_url=source,
        target_url=target,
        sent_by=sent_by,
    )
    _maybe_reschedule_handle_pending_webmentions()


def handle_outgoing_webmentions(absolute_url: str, text: str) -> None:
    """Delegate processing to `celery` if available, otherwise store for later.

    If settings.WEBMENTIONS_USE_CELERY is False, create a PendingOutgoingContent.
    This needs to be processed at some point by running `manage.py pending_mentions`.
    """
    use_celery = options.use_celery()

    if use_celery:
        _task_handle_outgoing.delay(absolute_url, text)

    else:
        PendingOutgoingContent.objects.get_or_create(
            absolute_url=absolute_url,
            defaults={
                "text": text,
            },
        )


@shared_task
def _task_handle_outgoing(absolute_url: str, text: str) -> None:
    process_outgoing_webmentions(source_urlpath=absolute_url, text=text)
    _maybe_reschedule_handle_pending_webmentions()


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
    allow_self_mentions = options.allow_self_mentions()

    for outgoing_retry in OutgoingWebmentionStatus.objects.filter(
        is_awaiting_retry=True,
    ):
        if not is_valid_target(
            outgoing_retry.target_url,
            allow_self_mention=allow_self_mentions,
        ):
            log.warning(f"Target URL is invalid: {outgoing_retry.target_url}")
            outgoing_retry.delete()
            continue

        if outgoing_retry.can_retry():
            try_send_webmention(
                source_urlpath=outgoing_retry.source_url,
                target_url=outgoing_retry.target_url,
                outgoing_status=outgoing_retry,
            )

    for pending_out in PendingOutgoingContent.objects.all():
        process_outgoing_webmentions(pending_out.absolute_url, pending_out.text)
        # OutgoingWebmentionStatus created instead to track status of individual links.
        pending_out.delete()


def _maybe_reschedule_handle_pending_webmentions():
    """Check if there are objects awaiting retry; if so, schedule `handle_pending_webmentions` to run again later."""
    should_reschedule = (
        PendingIncomingWebmention.objects.filter(is_awaiting_retry=True).exists()
        or OutgoingWebmentionStatus.objects.filter(is_awaiting_retry=True).exists()
    )

    if not should_reschedule:
        return

    _reschedule_handle_pending_webmentions()


def _reschedule_handle_pending_webmentions():
    """Using celery, schedule `handle_pending_webmentions` to run again later.

    Only one such task should be scheduled at a time - halt if it is already scheduled."""
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
        log.info(f"Task '{task_name}' already scheduled: ETA {scheduled_task_etas}")
        return

    # Schedule fresh task
    interval = options.retry_interval()
    task.apply_async(
        countdown=interval,
        expires=interval * 2,
    )
    log.info(f"Scheduled task '{task_name}' in {interval} seconds.")
