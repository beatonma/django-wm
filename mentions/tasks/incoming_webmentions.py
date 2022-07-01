import logging
from typing import Optional

import requests
from bs4 import Tag

from mentions.models.mixins.quotable import IncomingMentionType
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
    SourceDoesNotLink,
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


def _mark_as_failed(wm: Webmention, notes: _Notes) -> None:
    wm.notes = notes.join_to_string()[:999]
    wm.save()


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
        wm.target_object = obj

    except (TargetWrongDomain, TargetDoesNotExist):
        notes.warn(f"Unable to find matching page on our server for url '{target_url}'")

    except BadConfig:
        notes.warn(f"Unable to find a model associated with url '{target_url}'")

    # Verify that the source page exists and really contains a link
    # to the target
    try:
        response_text = _get_incoming_source_text(source_url)

    except SourceNotAccessible:
        return _mark_as_failed(
            wm,
            notes=notes.warn(f"Source not accessible: '{source_url}'"),
        )

    try:
        wm = _parse_source_html(wm, html=response_text, target_url=target_url)

    except SourceDoesNotLink:
        return _mark_as_failed(
            wm,
            notes=notes.info("Source does not contain a link to our content"),
        )

    wm.validated = True
    wm.notes = notes
    wm.save()


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


def _parse_source_html(wm: Webmention, html: str, target_url: str) -> Webmention:
    """Make sure that the source text really does link to the target_url and
    parse contextual data for webmention type, related h-card.

    Raises:
        SourceDoesNotLink: If the `target_url` does not appear in the given text.
    """

    soup = html_parser(html)
    link = soup.find("a", href=target_url)

    if link is None:
        raise SourceDoesNotLink()

    post_type = _parse_link_type(link)
    wm.post_type = post_type.name.lower() if post_type else None
    wm.hcard = HCard.from_soup(soup, save=True)
    return wm


def _parse_link_type(link: Tag) -> Optional[IncomingMentionType]:
    """Return any available type information in the context of the link.

    This may be available as a class on the link itself, or on a parent element
    that is marked with h-cite."""

    def find_mention_type_in_classlist(element: Tag) -> Optional[IncomingMentionType]:
        if element.has_attr("class"):
            classes = set(element["class"])

            for _type in IncomingMentionType.__members__.values():
                if _type.value in classes:
                    return _type

    link_type = find_mention_type_in_classlist(link)
    if link_type is not None:
        return link_type

    hcite = link.find_parent(class_="h-cite")
    if hcite:
        return find_mention_type_in_classlist(hcite)
