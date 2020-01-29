"""
Tests for webmentions that originate on our server, usually pointing somewhere else.
"""
import logging
from unittest import mock

import requests
from django.test import TestCase
from django.urls import reverse

from mentions.models import OutgoingWebmentionStatus
from mentions.tasks.outgoing_webmentions import _send_webmention
from mentions.tests.util import snippets
from mentions.tasks import (
    outgoing_webmentions,
    process_outgoing_webmentions,
)
from mentions.tests.util import functions
from mentions.tests.models import MentionableTestModel
from mentions.tests.util import constants

log = logging.getLogger(__name__)


OUTGOING_WEBMENTION_HTML = """<html>
<head><link rel="webmention" href="/webmention/" /></head>
<body>blah blah 
<a href="https://django-wm.dev/">This is a mentionable link</a> 
blah blah</body></html>
"""

OUTGOING_WEBMENTION_HTML_MULTIPLE_LINKS = """<html>
<head><link rel="webmention" href="/webmention/" /></head>
<body>blah blah 
<a href="https://django-wm.dev/">This is a mentionable link</a> 
<a href="https://django-wm.dev/some-article/">This is another mentionable link</a> 
blah blah</body></html>
"""

OUTGOING_WEBMENTION_HTML_NO_LINKS = """<html>
<head><link rel="webmention" href="/webmention/" /></head>
<body>blah blah no links here blah blah</body></html>
"""


class MockResponse:
    """Mock of requests.Response."""

    def __init__(
        self,
        url: str,
        headers: dict = None,
        text: str = None,
        status_code: int = None,
        *args,
        **kwargs,
    ):
        if headers is None:
            headers = {}

        self.url = url
        self.text = text
        self.status_code = status_code
        self.headers = headers

        if args:
            print(f"Unhandled args: {args}")
            self.args = args

        if kwargs:
            print(f"Unhandled kwargs: {kwargs}")
            self.kwargs = kwargs


def _get_mock_get_response_ok(url, *args, **kwargs):
    return {
        "https://django-wm.dev/": MockResponse(
            "https://django-wm.dev/",
            text=OUTGOING_WEBMENTION_HTML,
            headers=kwargs.get("headers", {}),
            status_code=200,
        ),
        "https://django-wm.dev/some-article/": MockResponse(
            "https://django-wm.dev/some-article/",
            text=OUTGOING_WEBMENTION_HTML_MULTIPLE_LINKS,
            headers=kwargs.get("headers", {}),
            status_code=200,
        ),
    }.get(url)


def _get_mock_post_response_ok(url, *args, **kwargs):
    return {
        "https://django-wm.dev/webmention/": MockResponse(
            "https://django-wm.dev/webmention/",
            headers=kwargs.get("headers", {}),
            status_code=200,
        ),
    }.get(url)


def _get_mock_post_response_endpoint_error(url, *args, **kwargs):
    return {
        "https://django-wm.dev/webmention/": MockResponse(
            "https://django-wm.dev/webmention/",
            text=OUTGOING_WEBMENTION_HTML,
            headers=kwargs.get("headers", {}),
            status_code=400,
        ),
    }.get(url)


class OutgoingWebmentionsTests(TestCase):
    """"""

    def setUp(self):
        self.target_stub_id, self.target_slug = functions.get_id_and_slug()

        target = MentionableTestModel.objects.create(
            stub_id=self.target_stub_id,
            slug=self.target_slug,
            allow_incoming_webmentions=True,
        )
        target.save()

    def _get_target_url(self, viewname):
        return reverse(viewname, args=[self.target_slug])

    def _get_absolute_target_url(self, viewname):
        return f"https://{constants.domain}{self._get_target_url(viewname)}"

    def test_find_links_in_text(self):
        """Ensure that outgoing links are found correctly."""

        outgoing_content = functions.get_mentioning_content(
            reverse(constants.view_all_endpoints, args=[self.target_slug])
        )

        outgoing_links = outgoing_webmentions._find_links_in_text(outgoing_content)
        self.assertEqual(
            outgoing_links, [functions.url(constants.correct_config, self.target_slug)]
        )

    def test_get_absolute_endpoint_from_response(self):
        """Ensure that any exposed endpoints are found and returned as an absolute url."""
        mock_response = MockResponse(
            url=self._get_absolute_target_url(constants.view_all_endpoints),
            headers={"Link": snippets.http_link_endpoint()},
        )
        absolute_endpoint_from_http_headers = outgoing_webmentions._get_absolute_endpoint_from_response(
            mock_response
        )
        self.assertEqual(
            constants.webmention_api_absolute_url, absolute_endpoint_from_http_headers
        )

        mock_response.headers = {}
        mock_response.text = snippets.html_head_endpoint()
        absolute_endpoint_from_html_head = outgoing_webmentions._get_absolute_endpoint_from_response(
            mock_response
        )
        self.assertEqual(
            constants.webmention_api_absolute_url, absolute_endpoint_from_html_head
        )

        mock_response.headers = {}
        mock_response.text = snippets.html_body_endpoint()
        absolute_endpoint_from_html_body = outgoing_webmentions._get_absolute_endpoint_from_response(
            mock_response
        )
        self.assertEqual(
            constants.webmention_api_absolute_url, absolute_endpoint_from_html_body
        )

    def test_get_endpoint_in_http_headers(self):
        """Ensure that endpoints exposed in http header are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(constants.view_all_endpoints),
            headers={"Link": snippets.http_link_endpoint()},
        )
        endpoint_from_http_headers = outgoing_webmentions._get_endpoint_in_http_headers(
            mock_response
        )
        self.assertEqual(
            constants.webmention_api_relative_url, endpoint_from_http_headers
        )

    def test_get_endpoint_in_html_head(self):
        """Ensure that endpoints exposed in html <head> are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(constants.view_all_endpoints),
            text=snippets.html_head_endpoint(),
        )
        endpoint_from_html_head = outgoing_webmentions._get_endpoint_in_html(
            mock_response
        )
        self.assertEqual(constants.webmention_api_relative_url, endpoint_from_html_head)

    def test_get_endpoint_in_html_body(self):
        """Ensure that endpoints exposed in html <body> are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(constants.view_all_endpoints),
            text=snippets.html_body_endpoint(),
        )
        endpoint_from_html_body = outgoing_webmentions._get_endpoint_in_html(
            mock_response
        )
        self.assertEqual(constants.webmention_api_relative_url, endpoint_from_html_body)

    def test_relative_to_absolute_url(self):
        """Ensure that relative urls are correctly converted to absolute"""

        domain = constants.domain
        page_url = f"https://{domain}/some-url-path"
        response = MockResponse(url=page_url)

        absolute_url_from_root = outgoing_webmentions._relative_to_absolute_url(
            response, "/webmention/"
        )
        self.assertEqual(f"https://{domain}/webmention/", absolute_url_from_root)

        absolute_url_from_relative = outgoing_webmentions._relative_to_absolute_url(
            response, "webmention/"
        )
        self.assertEqual(f"https://{domain}/webmention/", absolute_url_from_relative)

        already_absolute_url = outgoing_webmentions._relative_to_absolute_url(
            response, f"https://{domain}/already_absolute_path"
        )
        self.assertEqual(
            f"https://{domain}/already_absolute_path", already_absolute_url
        )

    @mock.patch.object(
        requests, "post", mock.Mock(side_effect=_get_mock_post_response_ok,)
    )
    def test_send_webmention(self):
        page_url = f"https://{constants.domain}/some-url-path/"
        success, status_code = _send_webmention(
            source_url=page_url,
            endpoint="https://django-wm.dev/webmention/",
            target="https://django-wm.dev/",
        )
        self.assertTrue(success)
        self.assertEqual(200, status_code)

    @mock.patch.object(
        requests, "post", mock.Mock(side_effect=_get_mock_post_response_endpoint_error,)
    )
    def test_send_webmention__with_endpoint_error(self):
        page_url = f"https://{constants.domain}/some-url-path/"
        success, status_code = _send_webmention(
            source_url=page_url,
            endpoint="https://django-wm.dev/webmention/",
            target="https://django-wm.dev/",
        )
        self.assertFalse(success)
        self.assertEqual(400, status_code)

    @mock.patch.object(
        requests, "get", mock.Mock(side_effect=_get_mock_get_response_ok,)
    )
    @mock.patch.object(
        requests, "post", mock.Mock(side_effect=_get_mock_post_response_ok,)
    )
    def test_process_outgoing_webmentions(self):
        """Test the entire process_outgoing_webmentions task."""
        self.assertEqual(0, OutgoingWebmentionStatus.objects.count())
        page_url = f"https://{constants.domain}/some-url-path/"
        page_text = OUTGOING_WEBMENTION_HTML

        wm = process_outgoing_webmentions(page_url, page_text)

        self.assertEqual(1, wm)
        self.assertEqual(1, OutgoingWebmentionStatus.objects.count())

        page_text = OUTGOING_WEBMENTION_HTML_MULTIPLE_LINKS
        wm = process_outgoing_webmentions(page_url, page_text)

        self.assertEqual(2, wm)
        self.assertEqual(3, OutgoingWebmentionStatus.objects.count())

    @mock.patch.object(
        requests,
        "get",
        mock.Mock(
            return_value=None,  # No network requests should be made if links not found in text
        ),
    )
    @mock.patch.object(
        requests,
        "post",
        mock.Mock(
            return_value=None,  # No network requests should be made if links not found in text
        ),
    )
    def test_process_outgoing_webmentions__with_no_links_found(self):
        """Test the entire process_outgoing_webmentions task with no links in provided text."""
        self.assertEqual(0, OutgoingWebmentionStatus.objects.count())
        page_url = f"https://{constants.domain}/some-url-path/"
        page_text = OUTGOING_WEBMENTION_HTML_NO_LINKS

        wm = process_outgoing_webmentions(page_url, page_text)

        self.assertEqual(0, wm)
        self.assertEqual(0, OutgoingWebmentionStatus.objects.count())

    @mock.patch.object(
        requests, "get", mock.Mock(side_effect=_get_mock_get_response_ok,)
    )
    @mock.patch.object(
        requests, "post", mock.Mock(side_effect=_get_mock_post_response_endpoint_error,)
    )
    def test_process_outgoing_webmentions__with_endpoint_error(self):
        """Test the entire process_outgoing_webmentions task."""
        self.assertEqual(0, OutgoingWebmentionStatus.objects.count())
        page_url = f"https://{constants.domain}/some-url-path/"
        page_text = OUTGOING_WEBMENTION_HTML

        wm = process_outgoing_webmentions(page_url, page_text)

        self.assertEqual(0, wm)
        self.assertEqual(1, OutgoingWebmentionStatus.objects.count())
