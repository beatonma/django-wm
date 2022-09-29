"""Asynchronous tasks that are handled by Celery."""
from .scheduling import (
    handle_incoming_webmention,
    handle_outgoing_webmentions,
    handle_pending_webmentions,
)
