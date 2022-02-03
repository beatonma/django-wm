import logging
import re
from typing import Optional, Set, Tuple
from urllib.parse import urlsplit

import requests

try:
    from celery import shared_task
    from celery.utils.log import get_task_logger

    log = get_task_logger(__name__)
except (ImportError, ModuleNotFoundError):
    from mentions.util import noop_shared_task

    shared_task = noop_shared_task
    log = logging.getLogger(__name__)

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from mentions.models import OutgoingWebmentionStatus
from mentions.util import html_parser

STATUS_MESSAGE_TARGET_UNREACHABLE = "The target URL could not be retrieved."
STATUS_MESSAGE_TARGET_ERROR_CODE = "The target URL returned an HTTP error code."
STATUS_MESSAGE_TARGET_ENDPOINT_ERROR = (
    "The target endpoint URL returned an HTTP error code"
)
STATUS_MESSAGE_OK = "The target server accepted the webmention."


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
def process_outgoing_webmentions(source_urlpath: str, text: str) -> int:
    """Find links and in the given text and submit a webmention to any servers that support them.

    Spec:
    https://www.w3.org/TR/webmention/#sender-discovers-receiver-webmention-endpoint

    For each link found in text:
        - Check that the link is alive
        - Search for webmention endpoint in:
            - HTTP response headers
            - HTML <head> element
            - HTML <body> element
        - If an endpoint is found, send a webmention notification

    source_urlpath should be the value returned by model.get_absolute_url() -
    it will be appended to settings.DOMAIN_NAME

    Returns:
         Number of outgoing webmentions that were submitted successfully.
    """

    log.info(f"Checking for outgoing webmention links...")
    mentions_attempted = 0
    mentions_sent = 0
    links_in_text = _find_links_in_text(text)

    if not links_in_text:
        log.debug("No links found in text.")
        return 0

    for link_url in links_in_text:
        result = _process_link(source_urlpath, link_url)

        if result is None:
            # No webmention endpoint found
            continue

        mentions_attempted += 1
        if result is True:
            mentions_sent += 1

    if mentions_sent == mentions_attempted:
        log.info(f"Successfully sent {mentions_sent} webmentions")

    elif mentions_attempted:
        log.warning(
            f"Webmention submission errors: {mentions_sent}/{mentions_attempted} submissions were successful"
        )

    else:
        log.info(f"No links with webmentionable endpoints were found.")

    return mentions_sent


def _process_link(source_urlpath: str, link_url: str) -> Optional[bool]:
    """Try to send a webmention for link_url.

    Returns:
        True if a webmention was submitted successfully.

        False if a webmention endpoint was resolved but submission failed.

        None if a webmention endpoint could not be resolved (i.e. the website does not appear to support webmentions).
    """
    outgoing_status = OutgoingWebmentionStatus.objects.create(
        source_url=source_urlpath,
        target_url=link_url,
    )

    # Confirm that the target url is alive
    log.debug(f"Checking url='{link_url}' for webmention support...")
    try:
        response = requests.get(link_url)
    except Exception as e:
        log.warning(f"Unable to fetch url={link_url}: {e}")
        _save_status(outgoing_status, STATUS_MESSAGE_TARGET_UNREACHABLE, success=False)
        return None

    if response.status_code >= 300:
        log.warning(
            f"Mentioned link '{link_url}' returned status={response.status_code}"
        )
        _save_status(
            outgoing_status,
            STATUS_MESSAGE_TARGET_ERROR_CODE,
            success=False,
            response_code=response.status_code,
        )
        return None

    endpoint = _get_absolute_endpoint_from_response(response)
    if endpoint:
        log.debug(f"Found webmention endpoint: '{endpoint}'")
        success, status_code = _send_webmention(source_urlpath, endpoint, link_url)
        if success:
            log.info(f"Webmention submission successful for '{link_url}'")
            _save_status(
                outgoing_status,
                STATUS_MESSAGE_OK,
                target_endpoint=endpoint,
                success=success,
                response_code=status_code,
            )
            return True

        else:
            log.warning(
                f"Webmention submission failed for '{link_url}' [endpoint={endpoint}]"
            )
            _save_status(
                outgoing_status,
                STATUS_MESSAGE_TARGET_ENDPOINT_ERROR,
                target_endpoint=endpoint,
                success=success,
                response_code=status_code,
            )
            return False
    else:
        log.info(f"No webmention endpoint found for url '{link_url}'")


def _find_links_in_text(text: str) -> Set[str]:
    soup = html_parser(text)
    return {a["href"] for a in soup.find_all("a", href=True)}


def _get_absolute_endpoint_from_response(response: requests.Response) -> Optional[str]:
    endpoint = _get_endpoint_in_http_headers(
        response
    ) or _get_endpoint_in_html_response(response)
    abs_url = _relative_to_absolute_url(response, endpoint)
    log.debug(f"Absolute url: {endpoint} -> {abs_url}")
    return abs_url


def _get_endpoint_in_html_response(response: requests.Response) -> Optional[str]:
    return _get_endpoint_in_html(response.text)


def _get_endpoint_in_http_headers(response: requests.Response) -> Optional[str]:
    """Search for webmention endpoint in HTTP headers."""
    try:
        header_link = response.headers.get("Link")
        if "webmention" in header_link:
            endpoint = re.match(
                r'<(?P<url>.*)>[; ]*.rel=[\'"]?webmention[\'"]?', header_link
            ).group(1)
            log.debug(f"Webmention endpoint found in HTTP header: '{endpoint}'")
            return endpoint
    except Exception as e:
        log.debug(f"Unable to read HTTP headers: {e}")


def _get_endpoint_in_html(html_text: str) -> Optional[str]:
    """Search for a webmention endpoint in HTML."""
    a_soup = html_parser(html_text)

    # Check HTML <head> for <link> webmention endpoint
    try:
        links = a_soup.head.find_all("link", href=True, rel=True)
        for link in links:
            if "webmention" in link["rel"]:
                endpoint = link["href"]
                log.debug(f"Webmention endpoint found in document head: {endpoint}")
                return endpoint
    except Exception as e:
        log.debug(f"Error reading <head> of external link: {e}")

    # Check HTML <body> for <a> webmention endpoint
    try:
        links = a_soup.body.find_all("a", href=True, rel=True)
        for link in links:
            if "webmention" in link["rel"]:
                endpoint = link["href"]
                log.debug(f"Webmention endpoint found in document body: {endpoint}")
                return endpoint
    except Exception as e:
        log.debug(f"Error reading <body> of link: {e}")


def _send_webmention(source_url: str, endpoint: str, target: str) -> Tuple[bool, int]:
    payload = {
        "target": target,
        "source": f"https://{settings.DOMAIN_NAME}{source_url}",
    }
    response = requests.post(endpoint, data=payload)
    status_code = response.status_code
    if status_code >= 300:
        log.warning(
            f'Sending webmention to "{endpoint}" '
            f"FAILED with status_code={status_code}"
        )
        return False, status_code
    else:
        log.info(
            f'Sending webmention to "{endpoint}" '
            f"successful with status_code={status_code}"
        )
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
        return f"{scheme}://{domain}/" f'{url if not url.startswith("/") else url[1:]}'
