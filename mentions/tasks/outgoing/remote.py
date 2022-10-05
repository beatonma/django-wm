import logging
import re
from typing import Optional, Tuple
from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import ValidationError
from requests import RequestException, Response

from mentions import options
from mentions.exceptions import TargetNotAccessible
from mentions.models import OutgoingWebmentionStatus
from mentions.resolution import get_or_create_outgoing_webmention
from mentions.util import get_url_validator, html_parser, http_get, http_post

__all__ = [
    "try_send_webmention",
]


STATUS_MESSAGE_TARGET_UNREACHABLE = "The target URL could not be retrieved: {error}."
STATUS_MESSAGE_TARGET_ERROR_CODE = (
    "The target URL returned an HTTP error code: {status_code}."
)
STATUS_MESSAGE_TARGET_ENDPOINT_ERROR = (
    "The target endpoint URL returned an HTTP error code"
)
STATUS_MESSAGE_OK = "The target server accepted the webmention."

log = logging.getLogger(__name__)


def try_send_webmention(
    source_urlpath: str,
    target_url: str,
    outgoing_status: Optional[OutgoingWebmentionStatus] = None,
) -> Optional[bool]:
    """Try to send a webmention for target_url.

    Returns:
        True if a webmention was submitted successfully.
        False if a webmention endpoint was resolved but submission failed.
        None if a webmention endpoint could not be resolved (i.e. the website does not appear to support webmentions).
    """
    if outgoing_status is None:
        outgoing_status = get_or_create_outgoing_webmention(source_urlpath, target_url)

    try:
        response = _get_target(outgoing_status, target_url)
    except TargetNotAccessible:
        return

    endpoint = _get_absolute_endpoint_from_response(response)
    if endpoint:
        log.debug(f"Found webmention endpoint: '{endpoint}'")
        return _try_send_webmention(
            outgoing_status,
            source_urlpath=source_urlpath,
            endpoint=endpoint,
            target_url=target_url,
        )

    else:
        log.info(f"No webmention endpoint found for url '{target_url}'")


def _get_target(
    status: OutgoingWebmentionStatus,
    target_url: str,
) -> Optional[Response]:
    """Confirm the target is accessible."""
    log.debug(f"Checking url='{target_url}' for webmention support...")
    try:
        response = http_get(target_url)
        if response.status_code < 300:
            return response

        error_message = STATUS_MESSAGE_TARGET_ERROR_CODE.format(
            status_code=response.status_code
        )

    except RequestException as e:
        error_message = STATUS_MESSAGE_TARGET_UNREACHABLE.format(error=e)

    _save_for_retry(
        status,
        error_message,
    )
    raise TargetNotAccessible()


def _try_send_webmention(
    status: OutgoingWebmentionStatus,
    source_urlpath: str,
    endpoint: str,
    target_url: str,
):
    success, status_code = _send_webmention(source_urlpath, endpoint, target_url)

    status.target_webmention_endpoint = endpoint
    status.response_code = status_code

    if success:
        log.info(f"Webmention submission successful for '{target_url}'")
        status.status_message = STATUS_MESSAGE_OK
        status.successful = True
        status.mark_processing_successful(save=True)
        return True

    else:
        log.warning(
            f"Webmention submission failed for '{target_url}' [endpoint={endpoint}]"
        )
        _save_for_retry(status, STATUS_MESSAGE_TARGET_ENDPOINT_ERROR)
        return False


def _send_webmention(
    source_urlpath: str,
    endpoint: str,
    target: str,
) -> Tuple[bool, int]:
    payload = {
        "target": target,
        "source": f"{options.url_scheme()}://{settings.DOMAIN_NAME}{source_urlpath}",
    }
    response = http_post(endpoint, data=payload)
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


def _get_absolute_endpoint_from_response(response: Response) -> Optional[str]:
    endpoint = _get_endpoint_in_http_headers(
        response
    ) or _get_endpoint_in_html_response(response)
    abs_url = _relative_to_absolute_url(response, endpoint)
    log.debug(f"Absolute url: {endpoint} -> {abs_url}")
    return abs_url


def _get_endpoint_in_html_response(response: Response) -> Optional[str]:
    return _get_endpoint_in_html(response.text)


def _get_endpoint_in_http_headers(response: Response) -> Optional[str]:
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


def _relative_to_absolute_url(response: Response, url: str) -> Optional[str]:
    """
    If given url is relative, try to construct an absolute url using response domain.
    """
    if not url:
        return None

    try:
        get_url_validator()(url)
        return url  # url is already well-formed.
    except ValidationError:
        scheme, domain, _, _, _ = urlsplit(response.url)
        if not scheme or not domain:
            return None
        return f"{scheme}://{domain}/" f'{url if not url.startswith("/") else url[1:]}'


def _save_for_retry(status: OutgoingWebmentionStatus, message: str) -> None:
    """In case of network errors, mark the status for reprocessing later."""
    log.warning(message)
    status.status_message = message
    status.mark_processing_failed(save=True)
