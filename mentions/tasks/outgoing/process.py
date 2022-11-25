from mentions.models.outgoing_status import get_or_create_outgoing_webmention
from mentions.tasks.celeryproxy import get_logger, shared_task
from mentions.tasks.outgoing.local import get_target_links_in_html
from mentions.tasks.outgoing.remote import try_send_webmention

log = get_logger(__name__)

__all__ = [
    "process_outgoing_webmentions",
]


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

    log.info(f"Checking for mentionable links in text from '{source_urlpath}'...")
    mentions_attempted = 0
    mentions_sent = 0
    links_in_text = get_target_links_in_html(text, source_path=source_urlpath)

    if not links_in_text:
        log.debug("No links found in text.")
        return 0

    for link_url in links_in_text:
        outgoing_webmention = get_or_create_outgoing_webmention(
            source_urlpath,
            link_url,
            reset_retries=True,
        )
        result = try_send_webmention(
            source_urlpath,
            link_url,
            outgoing_status=outgoing_webmention,
        )

        if result is None:
            # No webmention endpoint found
            continue

        mentions_attempted += 1
        if result is True:
            mentions_sent += 1

    if mentions_attempted == 0:
        log.debug(f"No mentionable links found in text.")

    elif mentions_sent == mentions_attempted:
        log.info(f"Successfully sent {mentions_sent} webmentions.")

    else:
        log.warning(
            f"Webmention submission errors: {mentions_sent}/{mentions_attempted} submissions were successful."
        )

    return mentions_sent
