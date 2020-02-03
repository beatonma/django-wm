from typing import Tuple
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db import models
from django.http import QueryDict

from mentions.exceptions import (
    BadConfig,
    TargetDoesNotExist,
    TargetWrongDomain,
    SourceNotAccessible,
)
from mentions.models import Webmention, HCard
from mentions.util import get_model_for_url_path

log = get_task_logger(__name__)


@shared_task
def process_incoming_webmention(http_post: QueryDict, client_ip: str) -> None:
    log.info(f'Processing webmention \'{http_post}\'')

    # Source and target have already been verified
    # as valid addresses before this method is called
    source = http_post['source']
    target = http_post['target']

    wm = Webmention.create(source, target, sent_by=client_ip)
    # wm.sent_by = client_ip

    # If anything fails, write it to notes and attach to webmention object
    # so it can be checked later
    notes = []

    # Check that the target page is accessible on our server and fetch
    # the corresponding object.
    try:
        obj = _get_target_object(target)
        log.info('Found webmention target object')
        wm.target_object = obj
    except (TargetWrongDomain, TargetDoesNotExist) as e:
        error_message = f'Unable to find matching page on our server {e}'
        log.warn(error_message)
        notes.append(error_message)
    except BadConfig as e:
        error_message = f'Unable to find a model associated with url {target}: {e}'
        log.warn(error_message)
        notes.append(error_message)

    # Verify that the source page exists and really contains a link
    # to the target
    try:
        response_text = _get_incoming_source(source)
    except SourceNotAccessible as e:
        log.warn(e)
        notes.append(f'Source not accessible: {e}')
        wm.notes = '\n'.join(notes)
        wm.save()
        return

    soup = BeautifulSoup(response_text, 'html.parser')
    if not soup.find('a', href=target):
        notes.append('Source does not contain a link to our content')
        wm.notes = '\n'.join(notes)
        wm.save()
        return

    hcard = HCard.from_soup(soup)
    if hcard:
        hcard.save()
        wm.hcard = hcard

    wm.validated = True
    wm.notes = '\n'.join(notes)

    wm.save()
    log.info(f'Webmention saved: {wm}')


def _get_target_path(target_url: str) -> Tuple[str, str, str]:
    scheme, full_domain, path, _, _ = urlsplit(target_url)
    domain = full_domain.split(':')[0]  # Remove port number if present
    return scheme, domain, path


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
    scheme, domain, path = _get_target_path(target_url)

    if domain not in settings.ALLOWED_HOSTS:
        raise TargetWrongDomain(f'Wrong domain: {domain} (from url={target_url})')

    try:
        return get_model_for_url_path(path)
    except BadConfig as e:
        log.warning(f'Failed to process incoming webmention! BAD CONFIG: {e}')
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
        raise SourceNotAccessible(f'Requests error: {e}')

    if response.status_code >= 300:
        raise SourceNotAccessible(
            f'Source \'{source_url}\' returned error code [{response.status_code}]')

    content_type = response.headers['content-type']
    if 'text/html' not in content_type:
        raise SourceNotAccessible(
            f'Source \'{source_url}\' returned unexpected content type: {content_type}')

    return response.text
