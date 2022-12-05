import logging

from mentions.exceptions import RejectedByConfig, SourceNotAccessible
from mentions.models import Webmention
from mentions.tasks.incoming.process import verify_webmention
from mentions.tasks.incoming.status import Status

log = logging.getLogger(__name__)


def reverify_mention(mention: Webmention):
    source_url = mention.source_url
    target_url = mention.target_url

    status = Status()

    try:
        is_verified, target_object, metadata = verify_webmention(
            source_url=source_url,
            target_url=target_url,
        )

    except RejectedByConfig as e:
        _mark_invalid(mention, status.warning(str(e)))
        return

    except SourceNotAccessible:
        _mark_invalid(
            mention, status.warning(f"Source URL not accessible: '{source_url}'")
        )
        return

    updated_fields = []

    if mention.target_object != target_object:
        log.info(f"Update target_object: {mention.target_object} -> {target_object}")
        mention.target_object = target_object
        updated_fields.append("target_object")

    if metadata:
        if mention.hcard != metadata.hcard:
            log.info(f"Update hcard: {mention.hcard} -> {metadata.hcard}")
            mention.hcard = metadata.hcard
            updated_fields.append("hcard")

        if mention.post_type != metadata.post_type:
            log.info(f"Update post_type: {mention.post_type} -> {metadata.post_type}")
            mention.post_type = metadata.post_type
            updated_fields.append("post_type")

    if mention.validated != is_verified:
        log.info(f"Update validated: {mention.validated} -> {is_verified}")
        mention.validated = is_verified
        updated_fields.append("validated")

    if updated_fields:
        updated_fields.append("notes")
        _append_notes(mention, status.info(f"Updated fields: {updated_fields}"))
        mention.save(update_fields=updated_fields)

    else:
        log.info("Webmention unchanged.")


def _mark_invalid(mention: Webmention, status: Status):
    mention.validated = False
    _append_notes(mention, status)
    mention.save()


def _append_notes(mention: Webmention, status: Status):
    mention.notes = "\n".join(
        [note for note in [mention.notes, *status.notes] if note]
    )[:1023]
