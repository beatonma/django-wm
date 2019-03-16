import requests

from bs4 import BeautifulSoup
from celery import shared_task
from celery.utils.log import get_task_logger
from urllib.parse import urlparse

from django.conf import settings

from mentions.exceptions import (
    BadConfig,
    TargetDoesNotExist,
    TargetWrongDomain,
    SourceNotAccessible,
)
from mentions.models import Webmention, HCard
from mentions.util import get_model_for_url


log = get_task_logger(__name__)


@shared_task
def process_incoming_webmention(http_post, client_ip):
    log.info('Processing webmention "{}"'.format(http_post))

    # Source and target have already been verified
    # as valid addresses before this method is called
    source = http_post['source']
    target = http_post['target']

    wm = Webmention.create(source, target)
    wm.sent_by = client_ip

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
        log.warn(f'Unable to find matching page on our server {e}')
        notes.append(f'Unable to find matching page on our server {e}')

    # Verify that the source page exists and really contains a link
    # to the target
    try:
        response = _get_incoming_source(source)
    except SourceNotAccessible as e:
        log.warn(e)
        notes.append(f'Source not accessible: {e}')
        wm.notes = '\n'.join(notes)
        wm.save()
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    if not soup.find('a', href=target):
        notes.append('Source does not contain a link to our content')
        wm.notes = '\n'.join(notes)
        wm.save()
        return

    wm.hcard = _get_hcard(soup)
    wm.validated = True
    wm.notes = '\n'.join(notes)

    wm.save()
    log.info(f'Webmention saved: {wm}')


def _get_target_object(target_url):
    r"""
    Confirm that the page exists on our server and return object.

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
    """
    url = urlparse(target_url)
    domain = url.netloc.split(':')[0]

    if domain not in settings.ALLOWED_HOSTS:
        raise TargetWrongDomain(f'Wrong domain: {domain}')

    try:
        return get_model_for_url(url.path)
    except BadConfig as e:
        log.critical(
            f'Failed to process incoming webmention! BAD CONFIG: {e}')
        raise(e)


def _get_incoming_source(source_url):
    """
    Fetch the source, confirm content is suitable and return response.
    Verify that the source URL returns an HTML page with a successful
    status code.
    """
    try:
        response = requests.get(source_url)
    except Exception as e:
        raise SourceNotAccessible(f'Requests error: {e}')

    if response.status_code >= 300:
        raise SourceNotAccessible(
            f'Source \'{source_url}\' returned error code [{response.status_code}]')

    content_type = response.headers['content-type']
    if 'text/html' not in content_type:
        raise SourceNotAccessible(
            f'Source \'{source_url}\' returned unexpected content type: {content_type}')

    return response


def _get_hcard(soup):
    """Return an HCard constructed from given soup content, or None."""
    hcard_element = soup.find(class_='h-card')
    if hcard_element:
        try:
            hcard = HCard.from_soup(soup)
        except Exception as e:
            log.error(e)
            raise(e)
        hcard.save()
        return hcard

    return None
