"""
Chunks of markup.
"""

import logging

from mentions.tests.util import constants

log = logging.getLogger(__name__)

BASE_HTML = """
<!DOCTYPE html>
<html lang="???">
<head>{head}</head>
<body>
{body}
</body>
</html>
"""


def build_html(head=None, body=None) -> str:
    return BASE_HTML.format(head=head, body=body)


def http_header_link(url):
    return f'<{url}>; rel="webmention"'


def _html_head_link(url):
    return f'<link rel="webmention" href="{url}"/>'


def _html_body_link(url):
    return f'<a rel="webmention" href="{url}">Endpoint!</a>'


def http_link_endpoint():
    return http_header_link(constants.webmention_api_relative_url)


def html_head_endpoint():
    return build_html(
        head=_html_head_link(constants.webmention_api_relative_url),
        body=None,
    )


def html_body_endpoint():
    return build_html(
        head=None,
        body=_html_body_link(constants.webmention_api_relative_url),
    )


def html_all_endpoints(content):
    return build_html(
        head=_html_head_link(constants.webmention_api_relative_url),
        body=f"""<div>{content}{_html_body_link(constants.webmention_api_relative_url)}This is arbitrary...</div>""",
    )
