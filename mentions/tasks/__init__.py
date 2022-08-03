"""Asynchronous tasks that are handled by Celery."""
from .incoming import process_incoming_webmention
from .outgoing import process_outgoing_webmentions
