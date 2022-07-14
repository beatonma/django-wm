from mentions.exceptions import (
    SourceDoesNotLink,
    SourceNotAccessible,
    TargetDoesNotExist,
    TargetWrongDomain,
)
from mentions.models import Webmention
from mentions.tasks.celeryproxy import get_logger, shared_task
from mentions.tasks.incoming.local import get_target_object
from mentions.tasks.incoming.remote import get_source_html, update_metadata_from_source

log = get_logger(__name__)


@shared_task
def process_incoming_webmention(source_url: str, target_url: str, sent_by: str) -> None:
    log.info(f"Processing webmention '{source_url}' -> '{target_url}'")

    wm = Webmention(source_url=source_url, target_url=target_url, sent_by=sent_by)
    notes = _Notes()

    try:
        wm.target_object = get_target_object(target_url)

    except (TargetWrongDomain, TargetDoesNotExist):
        notes.warn(f"Unable to find matching page on our server for url '{target_url}'")

    try:
        response_html = get_source_html(source_url)

    except SourceNotAccessible:
        return _save_mention(
            wm,
            notes=notes.warn(f"Source not accessible: '{source_url}'"),
        )

    try:
        wm = update_metadata_from_source(wm, html=response_html, target_url=target_url)

    except SourceDoesNotLink:
        return _save_mention(
            wm,
            notes=notes.warn("Source does not contain a link to our content"),
        )

    _save_mention(wm, notes, validated=True)


class _Notes:
    """Keep track of any issues that might need to be checked manually."""

    notes = []

    def warn(self, note) -> "_Notes":
        log.warning(note)
        self.notes.append(note)
        return self

    def join_to_string(self):
        return "\n".join(self.notes)

    def __str__(self):
        return "\n".join(self.notes)[:1023]


def _save_mention(wm: Webmention, notes: _Notes, validated: bool = False):
    wm.notes = str(notes)
    wm.validated = validated
    wm.save()
