import logging
import re
from typing import (
    Optional,
    Tuple,
    List,
)
from urllib.parse import urlsplit

from django.conf import settings

import requests

from bs4 import BeautifulSoup
from celery import shared_task
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from mentions.models import OutgoingWebmentionStatus

log = logging.getLogger(__name__)


STATUS_MESSAGE_TARGET_UNREACHABLE = 'The target URL could not be retrieved.'
STATUS_MESSAGE_TARGET_ERROR_CODE = 'The target URL returned an HTTP error code.'
STATUS_MESSAGE_TARGET_ENDPOINT_ERROR = 'The target endpoint URL returned an HTTP error code'
STATUS_MESSAGE_OK = 'The target server accepted the webmention.'


def _save_status(
        outgoing_status: OutgoingWebmentionStatus,
        message: str,
        success: bool,
        target_endpoint: Optional[str] = None,
        response_code: Optional[int] = None,
):
    outgoing_status.status_message = message
    outgoing_status.successful = success
    if target_endpoint:
        outgoing_status.target_webmention_endpoint = target_endpoint
    if response_code:
        outgoing_status.response_code = response_code
    outgoing_status.save()


@shared_task
def process_outgoing_webmentions(source_url: str, text: str) -> int:
    """
    Find links and send webmentions if remote server accepts them.

    Returns True if submissions is successful, False if submission fails, or
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
    log.info(f'Checking for outgoing webmention links...')
    mentions_sent = 0
    links_in_text = _find_links_in_text(text)

    if not links_in_text:
        log.info('No webmentionable links found in text.')
        log.debug(f'No webmentionable links in text [{text}]')
        return 0

    for link_url in links_in_text:
        outgoing_status = OutgoingWebmentionStatus.objects.create(
            source_url=source_url,
            target_url=link_url,
        )
        # Confirm that the target url is alive
        log.info(f'Checking url={link_url}')
        try:
            response = requests.get(link_url)
        except Exception as e:
            log.warning(f'Unable to fetch url={link_url}: {e}')
            _save_status(outgoing_status, STATUS_MESSAGE_TARGET_UNREACHABLE, success=False)
            continue

        if response.status_code >= 300:
            log.warning(
                f'Link "{link_url}" returned status={response.status_code}')
            _save_status(
                outgoing_status,
                STATUS_MESSAGE_TARGET_ERROR_CODE,
                success=False,
                response_code=response.status_code,
            )
            continue

        endpoint = _get_absolute_endpoint_from_response(response)
        if endpoint:
            log.info(f'Found webmention endpoint: {endpoint}')
            success, status_code = _send_webmention(source_url, endpoint, link_url)
            if success:
                mentions_sent += 1
                _save_status(
                    outgoing_status,
                    STATUS_MESSAGE_OK,
                    target_endpoint=endpoint,
                    success=success,
                    response_code=status_code,
                )
            else:
                _save_status(
                    outgoing_status,
                    STATUS_MESSAGE_TARGET_ENDPOINT_ERROR,
                    target_endpoint=endpoint,
                    success=success,
                    response_code=status_code,
                )
        else:
            log.info(f'No webmention endpoint found for url {link_url}')

    if mentions_sent:
        log.info(f'Successfully sent {mentions_sent} webmentions')
    else:
        log.info(f'No webmentions were successful!')

    return mentions_sent


def _find_links_in_text(text: str) -> List[str]:
    soup = BeautifulSoup(text, 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]


def _get_absolute_endpoint_from_response(response: requests.Response) -> Optional[str]:
    endpoint = (_get_endpoint_in_http_headers(response) or
                _get_endpoint_in_html(response))
    abs_url = _relative_to_absolute_url(response, endpoint)
    log.debug(f'Absolute url: {endpoint} -> {abs_url}')
    return abs_url


def _get_endpoint_in_http_headers(response: requests.Response) -> Optional[str]:
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


def _get_endpoint_in_html(response: requests.Response) -> Optional[str]:
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


def _send_webmention(source_url: str, endpoint: str, target: str) -> Tuple[bool, int]:
    payload = {
        'target': target,
        'source': f'https://{settings.DOMAIN_NAME}{source_url}'
    }
    log.info(f'{endpoint}: {payload}')
    response = requests.post(endpoint, data=payload)
    status_code = response.status_code
    if status_code >= 300:
        log.warning(f'Sending webmention to "{endpoint}" '
                    f'FAILED with status_code={status_code}')
        return False, status_code
    else:
        log.info(f'Sending webmention to "{endpoint}" '
                 f'successful with status_code={status_code}')
        return True, status_code


def _relative_to_absolute_url(response: requests.Response, url: str) -> Optional[str]:
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
