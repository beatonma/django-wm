from mentions import options
from mentions.exceptions import (
    SourceDoesNotLink,
    SourceNotAccessible,
    TargetDoesNotExist,
    TargetWrongDomain,
)
from mentions.models import PendingIncomingWebmention, Webmention
from mentions.tasks.celeryproxy import get_logger, shared_task
from mentions.tasks.incoming.local import get_target_object
from mentions.tasks.incoming.remote import get_metadata_from_source, get_source_html

__all__ = [
    "process_incoming_webmention",
]

log = get_logger(__name__)


@shared_task
def process_incoming_webmention(source_url: str, target_url: str, sent_by: str) -> None:
    log.info(f"Processing webmention '{source_url}' -> '{target_url}'")

    wm = Webmention(source_url=source_url, target_url=target_url, sent_by=sent_by)
    notes = _Notes()

    try:
        wm.target_object = get_target_object(target_url)

    except (TargetWrongDomain, TargetDoesNotExist):
        notes.warning(
            f"Unable to find matching page on our server for url '{target_url}'"
        )

    if wm.target_object is None and options.target_requires_model():
        log.warning(
            f"Ignoring received webmention [{source_url} -> {target_url}]: "
            "target does not resolve to a mentionable model instance."
        )
        return

    try:
        response_html = get_source_html(source_url)

    except SourceNotAccessible:
        return _save_for_retry(source_url, target_url, sent_by)

    try:
        wm = _get_metadata(wm, response_html, target_url, source_url)
        _save_mention(wm, notes, validated=True)

    except SourceDoesNotLink:
        _save_mention(
            wm,
            notes=notes.warning("Source does not contain a link to our content"),
        )


class _Notes:
    """Keep track of any issues that might need to be checked manually."""

    notes = []

    def warning(self, note) -> "_Notes":
        log.warning(note)
        self.notes.append(note)
        return self

    def __str__(self):
        return "\n".join(self.notes)[:1023]


def _save_mention(wm: Webmention, notes: _Notes, validated: bool = False):
    wm.notes = str(notes)
    wm.validated = validated
    wm.save()

    try:
        pending = PendingIncomingWebmention.objects.get(
            target_url=wm.target_url,
            source_url=wm.source_url,
        )
        pending.mark_processing_successful(save=True)
    except PendingIncomingWebmention.DoesNotExist:
        pass


def _save_for_retry(source_url: str, target_url: str, sent_by: str):
    """In case of network errors, create or update PendingIncomingWebmention instance to retry later."""
    log.info(f"_save_for_retry {source_url} -> {target_url}")

    pending, _ = PendingIncomingWebmention.objects.get_or_create(
        target_url=target_url,
        source_url=source_url,
        defaults={
            "sent_by": sent_by,
        },
    )

    pending.mark_processing_failed(save=True)


def _get_metadata(
    mention: Webmention, html: str, target_url: str, source_url: str
) -> Webmention:
    metadata = get_metadata_from_source(
        html=html,
        target_url=target_url,
        source_url=source_url,
    )
    mention.post_type = metadata.post_type
    mention.hcard = metadata.hcard
    return mention
