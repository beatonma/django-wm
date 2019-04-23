"""
Chunks of markup.
"""

import logging

from mentions.tests.util import constants

log = logging.getLogger(__name__)


def http_header_link(url):
    return f'<{url}>; rel="webmention"'


def html_head_link(url):
    return f'<link rel="webmention" href="{url}"/>'


def html_body_link(url):
    return f'<a rel="webmention" href="{url}">Endpoint!</a>'


def http_link_endpoint():
    return http_header_link(constants.webmention_api_relative_url)

def html_head_endpoint():
    return f'''
<html>
<head>
    {html_head_link(constants.webmention_api_relative_url)}
</head>
<body></body>
</html>
'''

def html_body_endpoint():
    return f'''
<html>
<head></head>
<body>
    {html_body_link(constants.webmention_api_relative_url)}
</body>
</html>
'''

def html_all_endpoints(content):
    return f'''
    <html>
    <head>
    {html_head_link(constants.webmention_api_relative_url)}
    </head>
    <body>
    <div>
    {content}
    </div>
    <div>
    {html_body_link(constants.webmention_api_relative_url)}
    </div>
    </body>
    </html>
'''
