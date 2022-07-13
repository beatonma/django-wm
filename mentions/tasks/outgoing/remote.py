import logging
import re
from typing import Optional, Tuple
from urllib.parse import urlsplit

import requests
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

log = logging.getLogger(__name__)


def try_send_webmention(source_urlpath: str, target_url: str) -> Optional[bool]:
    """Try to send a webmention for target_url.

    Returns:
        True if a webmention was submitted successfully.

        False if a webmention endpoint was resolved but submission failed.

        None if a webmention endpoint could not be resolved (i.e. the website does not appear to support webmentions).
    """
    outgoing_status = OutgoingWebmentionStatus.objects.create(
        source_url=source_urlpath,
        target_url=target_url,
    )

    # Confirm that the target url is alive
    log.debug(f"Checking url='{target_url}' for webmention support...")
    try:
        response = requests.get(target_url)
    except Exception as e:
        log.warning(f"Unable to fetch url={target_url}: {e}")
        _save_status(outgoing_status, STATUS_MESSAGE_TARGET_UNREACHABLE, success=False)
        return None

    if response.status_code >= 300:
        log.warning(
            f"Mentioned link '{target_url}' returned status={response.status_code}"
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
        success, status_code = _send_webmention(source_urlpath, endpoint, target_url)
        if success:
            log.info(f"Webmention submission successful for '{target_url}'")
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
                f"Webmention submission failed for '{target_url}' [endpoint={endpoint}]"
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
        log.info(f"No webmention endpoint found for url '{target_url}'")


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
