import logging

import requests

from mentions.resolution import get_model_for_url_path

try:
    from celery import shared_task
    from celery.utils.log import get_task_logger

    log = get_task_logger(__name__)
except (ImportError, ModuleNotFoundError):
    from mentions.util import noop_shared_task

    shared_task = noop_shared_task
    log = logging.getLogger(__name__)

from django.conf import settings

from mentions.exceptions import (
    BadConfig,
    SourceNotAccessible,
    TargetDoesNotExist,
    TargetWrongDomain,
)
from mentions.models import HCard, Webmention
from mentions.util import html_parser, split_url


class _Notes:
    notes = []

    def info(self, note) -> "_Notes":
        log.info(note)
        self.notes.append(note)
        return self

    def warn(self, note) -> "_Notes":
        log.warning(note)
        self.notes.append(note)
        return self

    def join_to_string(self):
        return "\n".join(self.notes)


def _update_wm(
    mention,
    target_object=None,
    notes: _Notes = None,
    hcard: HCard = None,
    validated: bool = None,
    save: bool = False,
):
    """Update a webmention with the given kwargs"""
    if target_object is not None:
        mention.target_object = target_object
    if notes is not None:
        mention.notes = notes.join_to_string()[:1000]
    if hcard is not None:
        mention.hcard = hcard
    if validated is not None:
        mention.validated = validated

    if save:
        mention.save()
        log.info(f"Webmention saved: {mention}")

    return mention


@shared_task
def process_incoming_webmention(source_url: str, target_url: str, sent_by: str) -> None:
    log.info(f"Processing webmention '{source_url}' -> '{target_url}'")

    wm = Webmention(source_url=source_url, target_url=target_url, sent_by=sent_by)

    # If anything fails, write it to notes and attach to webmention object
    # so it can be checked later
    notes = _Notes()

    # Check that the target page is accessible on our server and fetch
    # the corresponding object.
    try:
        obj = _get_target_object(target_url)
        notes.info("Found webmention target object")
        _update_wm(wm, target_object=obj)

    except (TargetWrongDomain, TargetDoesNotExist):
        notes.warn(f"Unable to find matching page on our server for url '{target_url}'")

    except BadConfig:
        notes.warn(f"Unable to find a model associated with url '{target_url}'")

    # Verify that the source page exists and really contains a link
    # to the target
    try:
        response_text = _get_incoming_source_text(source_url)

    except SourceNotAccessible:
        _update_wm(
            wm, notes=notes.warn(f"Source not accessible: '{source_url}'"), save=True
        )
        return

    soup = html_parser(response_text)
    if not soup.find("a", href=target_url):
        _update_wm(
            wm,
            notes=notes.info("Source does not contain a link to our content"),
            save=True,
        )
        return

    hcard = HCard.from_soup(soup, save=True)

    _update_wm(wm, validated=True, notes=notes, hcard=hcard, save=True)


def _get_target_object(target_url: str) -> "MentionableMixin":
    """Confirm that the page exists on our server and return object.

    Any mentionable Views must include the following kwargs:
        - 'model_name' - dotted python path to the model definition
                         This needs to be explicitely added to kwargs
        - 'slug'       - normally parsed from url pattern, used to
                         resolve the particular model instance

    e.g.
    re_path(
        r'^articles/(?P<slug>[\w\-]+)/?$',
        ArticleView.as_view(),
        kwargs={
            'model_name': 'core.models.Article',
        },
        name='app_view'),

    Raises:
        TargetWrongDomain: If the target_url points to a domain not listed in settings.ALLOWED_HOSTS
        BadConfig: Raised from get_model_for_url
    """
    scheme, domain, path = split_url(target_url)

    if domain not in settings.ALLOWED_HOSTS:
        raise TargetWrongDomain(f"Wrong domain: {domain} (from url={target_url})")

    try:
        return get_model_for_url_path(path)
    except BadConfig as e:
        raise e


def _get_incoming_source_text(source_url: str, client=requests) -> str:
    """Confirm source exists as HTML and return its text.

    Fetch the source, confirm content is suitable and return response.
    Verify that the source URL returns an HTML page with a successful
    status code.

    Args:
        source_url: The URL that mentions our content.
        client: A client for making HTTP requests. Should only be explicitly given when testing -
                its API is assumed to be equivalent to `python-requests`.

    Raises:
        SourceNotAccessible: If the `source_url` cannot be resolved, returns an error code, or
                             is an unexpected content type.
    """

    try:
        response = client.get(source_url)
    except Exception as e:
        raise SourceNotAccessible(f"Requests error: {e}")

    if response.status_code >= 300:
        raise SourceNotAccessible(
            f"Source '{source_url}' returned error code [{response.status_code}]"
        )

    content_type = response.headers["content-type"]  # Case-insensitive
    if "text/html" not in content_type:
        raise SourceNotAccessible(
            f"Source '{source_url}' returned unexpected content type: {content_type}"
        )

    return response.text
