"""Asynchronous tasks that are handled by Celery."""
from .incoming_webmentions import process_incoming_webmention
from .outgoing_webmentions import process_outgoing_webmentions
