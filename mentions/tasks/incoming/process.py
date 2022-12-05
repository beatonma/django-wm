from typing import Optional, Tuple, Union

from mentions import options
from mentions.exceptions import (
    RejectedByConfig,
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
    "verify_webmention",
]

from mentions.tasks.incoming.status import Status

log = get_logger(__name__)


@shared_task
def process_incoming_webmention(source_url: str, target_url: str, sent_by: str) -> None:
    log.info(f"Processing webmention '{source_url}' -> '{target_url}'")

    status = Status()

    try:
        is_verified, target_object, metadata = verify_webmention(
            source_url=source_url, target_url=target_url
        )

    except RejectedByConfig:
        log.warning(
            f"Ignoring received webmention [{source_url} -> {target_url}]: "
            "target does not resolve to a mentionable model instance."
        )
        return

    except SourceNotAccessible:
        _save_for_retry(source_url, target_url, sent_by)
        return

    if not is_verified:
        status.warning(f"Source does not contain a link to '{target_url}'")

    _create_webmention(
        source_url=source_url,
        target_url=target_url,
        sent_by=sent_by,
        target_object=target_object,
        verified=is_verified,
        metadata=metadata,
        notes=status,
    )
    _mark_complete(source_url, target_url)


def verify_webmention(
    source_url: str,
    target_url: str,
) -> Tuple[bool, Optional[MentionableMixin], Optional[WebmentionMetadata]]:
    """If the returned metadata is None, verification"""
    is_verified = False

    try:
        target_object = get_target_object(target_url)

    except TargetWrongDomain:
        log.warning(
            f"Received webmention does not target our domain: {source_url} -> {target_url}"
        )
        raise

    except TargetDoesNotExist:
        target_object = None

    if target_object is None and options.target_requires_model():
        log.warning(
            f"Ignoring received webmention [{source_url} -> {target_url}]: "
            "target does not resolve to a mentionable model instance."
        )
        raise RejectedByConfig(f"No target_object found for url={target_url}")

    try:
        response_html = get_source_html(source_url)

    except SourceNotAccessible:
        raise

    try:
        metadata = get_metadata_from_source(response_html, target_url, source_url)
        is_verified = True
    except SourceDoesNotLink:
        metadata = None

    return is_verified, target_object, metadata


def _create_webmention(
    source_url: str,
    target_url: str,
    sent_by: str,
    verified: bool,
    target_object: Optional[MentionableMixin],
    metadata: Optional[WebmentionMetadata],
    notes: Union[Status, str] = "",
) -> Webmention:
    return Webmention.objects.create(
        source_url=source_url,
        target_url=target_url,
        sent_by=sent_by,
        target_object=target_object,
        validated=verified,
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
