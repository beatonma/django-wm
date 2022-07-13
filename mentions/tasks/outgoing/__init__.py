import logging

from mentions.tasks.outgoing.local import get_target_links_in_text
from mentions.tasks.outgoing.remote import try_send_webmention

try:
    from celery import shared_task
    from celery.utils.log import get_task_logger

    log = get_task_logger(__name__)
except (ImportError, ModuleNotFoundError):
    from mentions.util import noop_shared_task

    shared_task = noop_shared_task
    log = logging.getLogger(__name__)


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
    links_in_text = get_target_links_in_text(text)

    if not links_in_text:
        log.debug("No links found in text.")
        return 0

    for link_url in links_in_text:
        result = try_send_webmention(source_urlpath, link_url)

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
