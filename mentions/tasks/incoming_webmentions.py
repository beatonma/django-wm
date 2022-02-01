import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db import models
from django.http import QueryDict

from mentions.exceptions import (
    BadConfig,
    SourceNotAccessible,
    TargetDoesNotExist,
    TargetWrongDomain,
)
from mentions.models import HCard, Webmention
from mentions.util import get_model_for_url_path, html_parser, split_url

log = get_task_logger(__name__)


class Notes:
    notes = []

    def info(self, note) -> "Notes":
        log.info(note)
        self.notes.append(note)
        return self

    def warn(self, note) -> "Notes":
        log.warning(note)
        self.notes.append(note)
        return self

    def join_to_string(self):
        return "\n".join(self.notes)


def _update_wm(
    mention,
    target_object=None,
    notes: Notes = None,
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
        log.info(f"Webmention saved: {mention}")
        mention.save()

    return mention


@shared_task
def process_incoming_webmention(http_post: QueryDict, client_ip: str) -> None:
    log.info(f"Processing webmention '{http_post}'")

    # Source and target have already been verified
    # as valid addresses before this method is called
    source = http_post["source"]
    target = http_post["target"]

    wm = Webmention(source_url=source, target_url=target, sent_by=client_ip)

    # If anything fails, write it to notes and attach to webmention object
    # so it can be checked later
    notes = Notes()

    # Check that the target page is accessible on our server and fetch
    # the corresponding object.
    try:
        obj = _get_target_object(target)
        notes.info("Found webmention target object")
        _update_wm(wm, target_object=obj)

    except (TargetWrongDomain, TargetDoesNotExist):
        notes.warn(f"Unable to find matching page on our server for url '{target}'")

    except BadConfig:
        notes.warn(f"Unable to find a model associated with url '{target}'")

    # Verify that the source page exists and really contains a link
    # to the target
    try:
        response_text = _get_incoming_source(source)

    except SourceNotAccessible:
        _update_wm(
            wm, notes=notes.warn(f"Source not accessible: '{source}'"), save=True
        )
        return

    soup = html_parser(response_text)
    if not soup.find("a", href=target):
        _update_wm(
            wm,
            notes=notes.info("Source does not contain a link to our content"),
            save=True,
        )
        return

    hcard = HCard.from_soup(soup, save=True)

    _update_wm(wm, validated=True, notes=notes, hcard=hcard, save=True)


def _get_target_object(target_url: str) -> models.Model:
    r"""
    Confirm that the page exists on our server and return object.
    Throws

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


def _get_incoming_source(source_url: str, client=requests) -> str:
    """
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

    content_type = response.headers["content-type"]
    if "text/html" not in content_type:
        raise SourceNotAccessible(
            f"Source '{source_url}' returned unexpected content type: {content_type}"
        )

    return response.text
