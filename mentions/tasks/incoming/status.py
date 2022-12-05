import logging

from django.utils import timezone

log = logging.getLogger(__name__)


class Status:
    """Keep track of any issues that might need to be checked manually."""

    def __init__(self):
        self.notes = []
        self.ok = True

    def info(self, note: str):
        log.info(note)
        self._append(note, "I")
        return self

    def error(self, note: str):
        self.ok = False
        log.error(note)
        self._append(note, "E")
        return self

    def warning(self, note: str) -> "Status":
        log.warning(note)
        self._append(note, "W")
        return self

    def _append(self, note: str, level: str):
        timestamp = timezone.now().strftime("%Y-%m-%d/%H:%M")
        self.notes.append(f"{level}/{timestamp}: {note}")

    def __str__(self):
        return "\n".join(self.notes)[:1023]
