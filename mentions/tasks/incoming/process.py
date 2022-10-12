from typing import Optional, Union

from mentions import options
from mentions.exceptions import (
    SourceDoesNotLink,
    SourceNotAccessible,
    TargetDoesNotExist,
    TargetWrongDomain,
)
from mentions.models import PendingIncomingWebmention, Webmention
from mentions.models.mixins import MentionableMixin
from mentions.tasks.celeryproxy import get_logger, shared_task
from mentions.tasks.incoming.local import get_target_object
from mentions.tasks.incoming.remote import (
    WebmentionMetadata,
    get_metadata_from_source,
    get_source_html,
)

__all__ = [
    "process_incoming_webmention",
]

log = get_logger(__name__)


@shared_task
def process_incoming_webmention(source_url: str, target_url: str, sent_by: str) -> None:
    log.info(f"Processing webmention '{source_url}' -> '{target_url}'")

    status = Status()

    try:
        target_object = get_target_object(target_url)

    except TargetWrongDomain:
        log.warning(
            f"Received webmention does not target our domain: {source_url} -> {target_url}"
        )
        return

    except TargetDoesNotExist:
        target_object = None

    if target_object is None and options.target_requires_model():
        log.warning(
            f"Ignoring received webmention [{source_url} -> {target_url}]: "
            "target does not resolve to a mentionable model instance."
        )
        return

    try:
        response_html = get_source_html(source_url)

    except SourceNotAccessible:
        return _save_for_retry(source_url, target_url, sent_by)

    webmention_kwargs = {
        "source_url": source_url,
        "target_url": target_url,
        "sent_by": sent_by,
        "target_object": target_object,
    }

    try:
        metadata = get_metadata_from_source(response_html, target_url, source_url)
        _create_webmention(
            **webmention_kwargs,
            validated=True,
            metadata=metadata,
            notes=status,
        )

    except SourceDoesNotLink:
        _create_webmention(
            **webmention_kwargs,
            validated=False,
            metadata=None,
            notes=status.warning(f"Source does not contain a link to '{target_url}'"),
        )

    _mark_complete(source_url, target_url)


class Status:
    """Keep track of any issues that might need to be checked manually."""

    def __init__(self):
        self.notes = []
        self.ok = True

    def error(self, note: str):
        self.ok = False
        return self.warning(note)

    def warning(self, note: str) -> "Status":
        log.warning(note)
        self.notes.append(note)
        return self

    def __str__(self):
        return "\n".join(self.notes)[:1023]


def _create_webmention(
    source_url: str,
    target_url: str,
    sent_by: str,
    validated: bool,
    target_object: Optional[MentionableMixin],
    metadata: Optional[WebmentionMetadata],
    notes: Union[Status, str] = "",
) -> Webmention:
    return Webmention.objects.create(
        source_url=source_url,
        target_url=target_url,
        sent_by=sent_by,
        target_object=target_object,
        validated=validated,
        hcard=metadata.hcard if metadata else None,
        post_type=metadata.post_type if metadata else None,
        notes=str(notes),
    )


def _mark_complete(source_url: str, target_url: str):
    try:
        pending = PendingIncomingWebmention.objects.get(
            target_url=target_url,
            source_url=source_url,
        )
        pending.mark_processing_successful(save=True)
    except PendingIncomingWebmention.DoesNotExist:
        pass


def _save_for_retry(source_url: str, target_url: str, sent_by: str):
    """In case of network errors, create or update PendingIncomingWebmention instance to retry later."""
    pending, _ = PendingIncomingWebmention.objects.get_or_create(
        target_url=target_url,
        source_url=source_url,
        defaults={
            "sent_by": sent_by,
        },
    )

    pending.mark_processing_failed(save=True)
