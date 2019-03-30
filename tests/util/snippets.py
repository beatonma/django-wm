"""
Chunks of markup.
"""

import logging

from mentions.tests.util.constants import webmention_api_relative_url

log = logging.getLogger(__name__)


def http_header_link(url):
    return f'<{url}>; rel="webmention"'


def html_head_link(url):
    return f'<link rel="webmention" href="{url}"/>'


def html_body_link(url):
    return f'<a rel="webmention" href="{url}">Endpoint!</a>'


HTTP_LINK_ENDPOINT = http_header_link(webmention_api_relative_url)
HTML_HEAD_ENDPOINT = f'''
<html>
<head>
    {html_head_link(webmention_api_relative_url)}
</head>
<body></body>
</html>
'''
HTML_BODY_ENDPOINT = f'''
<html>
<head></head>
<body>
    {html_body_link(webmention_api_relative_url)}
</body>
</html>
'''
