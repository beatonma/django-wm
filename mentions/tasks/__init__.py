"""Asynchronous tasks that are handled by Celery."""
from .incoming_webmentions import process_incoming_webmention
from .outgoing import process_outgoing_webmentions
