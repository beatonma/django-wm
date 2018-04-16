import re

from django.conf import settings

import requests

from bs4 import BeautifulSoup
from celery import shared_task
from celery.utils.log import get_task_logger


log = get_task_logger(__name__)


@shared_task
def process_outgoing_webmentions(source_url, text):
    """
    Find links and send webmentions if remote server accepts them.

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
    self_soup = BeautifulSoup(text, 'html.parser')
    for a in self_soup.find_all('a', href=True):
        href = a['href']

        # Confirm that the target url is alive
        try:
            response = requests.get(href)
        except Exception as e:
            log.warn('Unable to fetch url={}: {}'.format(href, e))
            return

        if response.status_code >= 300:
            log.warn('Link "{}" returned status_code={}'
                     .format(response.status_code))
            return

        endpoint = _get_endpoint_from_response(response)
        if endpoint:
            _send_webmention(source_url, endpoint, href)


def _get_endpoint_from_response(response):
    endpoint = (_get_endpoint_in_http_headers(response) or
                _get_endpoint_in_html(response))
    return endpoint


def _get_endpoint_in_http_headers(response):
    """Search for webmention endpoint in HTTP headers."""
    try:
        header_link = response.headers['Link']
        if 'webmention' in header_link:
            log.debug('webmention endpoint found in http header')
            endpoint = re.match(
                '<(?P<url>.*)>[; ]*.rel=[\'"]webmention[\'"]',
                header_link).group(1)
            return endpoint
    except Exception as e:
        log.debug('Error reading http headers: {}'.format(e))


def _get_endpoint_in_html(response):
    """Search for a webmention endpoint in HTML."""
    a_soup = BeautifulSoup(response.text, 'html.parser')

    # Check HTML <head> for <link> webmention endpoint
    try:
        links = a_soup.head.find_all('link', href=True, rel=True)
        for link in links:
            if 'webmention' in link['rel']:
                log.debug(
                    'webmention endpoint found in document head - address={}'
                    .format(link['href']))
                endpoint = link['href']
                return endpoint
    except Exception as e:
        log.debug('Error reading <head> of external link: {}'
                  .format(e))

    # Check HTML <body> for <a> webmention endpoint
    try:
        links = a_soup.body.find_all('a', href=True, rel=True)
        for link in links:
            if 'webmention' in link['rel']:
                log.debug('webmention endpoint found in document body')
                endpoint = link['href']
                return endpoint
    except Exception as e:
        log.debug('Error reading <body> of link: {}'.format(e))


def _send_webmention(source_url, endpoint, target):
    payload = {
        'target': target,
        'source': '{}{}'.format(
            settings.DOMAIN_NAME, source_url)
    }
    log.info('{}: {}'.format(endpoint, payload))
    response = requests.post(endpoint, data=payload)
    status_code = response.status_code
    if status_code >= 300:
        log.warn('Sending webmention to "{}" FAILED with status_code={}'
                 .format(endpoint, status_code))
    else:
        log.info('Sending webmention to "{}" successful with status_code={}'
                 .format(endpoint, status_code))
