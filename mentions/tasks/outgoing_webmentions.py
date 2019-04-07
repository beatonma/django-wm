import re
from urllib.parse import urlsplit

from django.conf import settings

import requests

from bs4 import BeautifulSoup
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

log = get_task_logger(__name__)


@shared_task
def process_outgoing_webmentions(source_url: str, text: str):
    """
    Find links and send webmentions if remote server accepts them.

    Returns True if submissions is successful, False if submissino fails, or
    None if no endpoints were found.


    Spec:
    https://www.w3.org/TR/webmention/#sender-discovers-receiver-webmention-endpoint

    For each link found in text:
        - Check that the link is alive
        - Search for webmention endpoint in:
            - HTTP response headers
            - HTML <head> element
            - HTML <body> element
        - If an endpoint is found, send a webmention notification

    source_url should be the value returned by model.get_absolute_url() -
    it will be appended to settings.DOMAIN_NAME
    """
    log.info('Checking for outgoing webmention links...')
    for link_url in _find_links_in_text(text):
        # Confirm that the target url is alive
        try:
            response = requests.get(link_url)
        except Exception as e:
            log.warn(f'Unable to fetch url={link_url}: {e}')
            return None

        if response.status_code >= 300:
            log.warn(
                f'Link "{link_url}" returned status={response.status_code}')
            return None

        endpoint = _get_absolute_endpoint_from_response(response)
        if endpoint:
            return _send_webmention(source_url, endpoint, link_url)
        return None


def _find_links_in_text(text: str):
    soup = BeautifulSoup(text, 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]


def _get_absolute_endpoint_from_response(response) -> str:
    endpoint = (_get_endpoint_in_http_headers(response) or
                _get_endpoint_in_html(response))
    abs_url = _relative_to_absolute_url(response, endpoint)
    log.debug(f'Absolute url: {endpoint} -> {abs_url}')
    return abs_url


def _get_endpoint_in_http_headers(response) -> str:
    """Search for webmention endpoint in HTTP headers."""
    try:
        header_link = response.headers.get('Link')
        if 'webmention' in header_link:
            log.debug('webmention endpoint found in http header')
            endpoint = re.match(
                r'<(?P<url>.*)>[; ]*.rel=[\'"]?webmention[\'"]?',
                header_link).group(1)
            return endpoint
    except Exception as e:
        log.debug(f'Error reading http headers: {e}')


def _get_endpoint_in_html(response) -> str:
    """Search for a webmention endpoint in HTML."""
    a_soup = BeautifulSoup(response.text, 'html.parser')

    # Check HTML <head> for <link> webmention endpoint
    try:
        links = a_soup.head.find_all('link', href=True, rel=True)
        for link in links:
            if 'webmention' in link['rel']:
                endpoint = link['href']
                log.debug(
                    f'webmention endpoint found in document head - '
                    f'address={endpoint}')
                endpoint = link['href']
                return endpoint
    except Exception as e:
        log.debug(f'Error reading <head> of external link: {e}')

    # Check HTML <body> for <a> webmention endpoint
    try:
        links = a_soup.body.find_all('a', href=True, rel=True)
        for link in links:
            if 'webmention' in link['rel']:
                log.debug('webmention endpoint found in document body')
                endpoint = link['href']
                return endpoint
    except Exception as e:
        log.debug(f'Error reading <body> of link: {e}')


def _send_webmention(source_url: str, endpoint: str, target: str):
    payload = {
        'target': target,
        'source': f'{settings.DOMAIN_NAME}{source_url}'
    }
    log.info(f'{endpoint}: {payload}')
    response = requests.post(endpoint, data=payload)
    status_code = response.status_code
    if status_code >= 300:
        log.warn(f'Sending webmention to "{endpoint}" '
                 f'FAILED with status_code={status_code}')
        return False
    else:
        log.info(f'Sending webmention to "{endpoint}" '
                 f'successful with status_code={status_code}')
        return True


def _relative_to_absolute_url(response, url: str) -> str:
    """
    If given url is relative, try to construct an absolute url using response domain.
    """
    if not url:
        return None

    try:
        URLValidator()(url)
        return url  # url is already well-formed.
    except ValidationError:
        scheme, domain, _, _, _ = urlsplit(response.url)
        if not scheme or not domain:
            return None
        return f'{scheme}://{domain}/' \
            f'{url if not url.startswith("/") else url[1:]}'
