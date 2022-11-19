"""Chunks of markup."""

import logging

from tests.tests.util import testfunc

log = logging.getLogger(__name__)

BASE_HTML = """
<!DOCTYPE html>
<html lang="en-GB">
<head>{head}</head>
<body>
{body}
</body>
</html>
"""


def build_html(head=None, body=None) -> str:
    return BASE_HTML.format(head=head or "", body=body or "")


def http_header_link(url, **kwargs):
    attrs = "; ".join(
        [
            f"""{name}="{value}\"""" if value else f"{name}"
            for name, value in kwargs.items()
        ]
    )

    return f"<{url}>; {attrs}"


def _html_head_link(url):
    return f'<link rel="webmention" href="{url}"/>'


def _html_body_link(url):
    return f'<a rel="webmention" href="{url}">Endpoint!</a>'


def http_link_endpoint():
    return http_header_link(testfunc.endpoint_submit_webmention(), rel="webmention")


def html_head_endpoint():
    return build_html(
        head=_html_head_link(testfunc.endpoint_submit_webmention()),
        body=None,
    )


def html_body_endpoint():
    return build_html(
        head=None,
        body=_html_body_link(testfunc.endpoint_submit_webmention()),
    )


def html_all_endpoints(content):
    return build_html(
        head=_html_head_link(testfunc.endpoint_submit_webmention()),
        body=f"""<div>{content}
        {_html_body_link(testfunc.endpoint_submit_webmention())}
        This is arbitrary...</div>""",
    )


def html_with_mentions(*urls: str) -> str:
    html_link = """<a href="{url}">This is a mentionable link</a>"""
    links = [html_link.format(url=u) for u in urls]

    return build_html(
        head=_html_head_link(testfunc.endpoint_submit_webmention()),
        body="".join(links),
    )
