"""
Tests for webmentions that originate on our server, usually pointing somewhere else.
"""
import logging
from unittest.mock import Mock, patch

import requests
from django.conf import settings

from mentions.models import OutgoingWebmentionStatus
from mentions.tasks import outgoing_webmentions, process_outgoing_webmentions
from mentions.tests import WebmentionTestCase
from mentions.tests.util import snippets, testfunc

log = logging.getLogger(__name__)


TARGET_DOMAIN = testfunc.random_domain()

OUTGOING_WEBMENTION_HTML = f"""<html>
<head><link rel="webmention" href="/webmention/" /></head>
<body>blah blah 
<a href="https://{TARGET_DOMAIN}/">This is a mentionable link</a> 
blah blah</body></html>
"""

OUTGOING_WEBMENTION_HTML_MULTIPLE_LINKS = f"""<html>
<head><link rel="webmention" href="/webmention/" /></head>
<body>blah blah 
<a href="https://{TARGET_DOMAIN}/">This is a mentionable link</a> 
<a href="https://{TARGET_DOMAIN}/some-article/">This is another mentionable link</a> 
blah blah</body></html>
"""

OUTGOING_WEBMENTION_HTML_NO_LINKS = """<html>
<head><link rel="webmention" href="/webmention/" /></head>
<body>blah blah no links here blah blah</body></html>
"""

OUTGOING_WEBMENTION_HTML_DUPLICATE_LINKS = f"""<html>
<head><link rel="webmention" href="/webmention/" /></head>
<body>blah blah 
<a href="https://beatonma.org/">This is a mentionable link</a> 
blah blah duplicate links
<a href="https://snommoc.org/">This is some other link</a> 
<a href="https://beatonma.org/">This is a duplicate link</a> 
</body></html>
"""


class MockResponse:
    """Mock of requests.Response."""

    def __init__(
        self,
        url: str,
        headers: dict = None,
        text: str = None,
        status_code: int = None,
    ):
        self.url = url
        self.text = text
        self.status_code = status_code
        self.headers = headers


def _mock_get_ok(url, headers=None, **kwargs):
    return {
        f"https://{TARGET_DOMAIN}/": MockResponse(
            url,
            text=OUTGOING_WEBMENTION_HTML,
            headers=headers,
            status_code=200,
        ),
        f"https://{TARGET_DOMAIN}/some-article/": MockResponse(
            url,
            text=OUTGOING_WEBMENTION_HTML_MULTIPLE_LINKS,
            headers=headers,
            status_code=200,
        ),
    }.get(url)


def _mock_post_ok(url, headers=None, **kwargs):
    return {
        f"https://{TARGET_DOMAIN}/webmention/": MockResponse(
            url,
            headers=headers,
            status_code=200,
        ),
    }.get(url)


def _mock_post_error(url, headers=None, **kwargs):
    return {
        f"https://{TARGET_DOMAIN}/webmention/": MockResponse(
            url,
            text=OUTGOING_WEBMENTION_HTML,
            headers=headers,
            status_code=400,
        ),
    }.get(url)


def _patch_get(ok: bool):
    return patch.object(requests, "get", Mock(side_effect=_mock_get_ok if ok else None))


def _patch_post(ok: bool):
    return patch.object(
        requests, "post", Mock(side_effect=_mock_post_ok if ok else _mock_post_error)
    )


class EndpointDiscoveryTests(WebmentionTestCase):
    """Outgoing webmentions: Endpoint discovery & resolution"""

    absolute_endpoint = testfunc.endpoint_submit_webmention_absolute()
    relative_endpoint = testfunc.endpoint_submit_webmention()

    def setUp(self):
        target_pk, self.target_slug = testfunc.get_id_and_slug()

    def _get_absolute_target_url(self):
        return testfunc.get_url(self.target_slug)

    def test_get_absolute_endpoint_from_response(self):
        """Any exposed endpoints (in HTTP header, HTML <head> or <body>) are found and returned as an absolute url."""
        mock_response = MockResponse(
            url=self._get_absolute_target_url(),
            headers={"Link": snippets.http_link_endpoint()},
        )
        absolute_endpoint_from_http_headers = (
            outgoing_webmentions._get_absolute_endpoint_from_response(mock_response)
        )
        self.assertEqual(self.absolute_endpoint, absolute_endpoint_from_http_headers)

        mock_response.headers = {}
        mock_response.text = snippets.html_head_endpoint()
        absolute_endpoint_from_html_head = (
            outgoing_webmentions._get_absolute_endpoint_from_response(mock_response)
        )
        self.assertEqual(self.absolute_endpoint, absolute_endpoint_from_html_head)

        mock_response.headers = {}
        mock_response.text = snippets.html_body_endpoint()
        absolute_endpoint_from_html_body = (
            outgoing_webmentions._get_absolute_endpoint_from_response(mock_response)
        )
        self.assertEqual(self.absolute_endpoint, absolute_endpoint_from_html_body)

    def test_get_endpoint_in_http_headers(self):
        """Endpoints exposed in HTTP header are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(),
            headers={"Link": snippets.http_link_endpoint()},
        )
        endpoint_from_http_headers = outgoing_webmentions._get_endpoint_in_http_headers(
            mock_response
        )
        self.assertEqual(self.relative_endpoint, endpoint_from_http_headers)

    def test_get_endpoint_in_html_head(self):
        """Endpoints exposed in HTML <head> are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(),
            text=snippets.html_head_endpoint(),
        )
        endpoint_from_html_head = outgoing_webmentions._get_endpoint_in_html(
            mock_response
        )
        self.assertEqual(self.relative_endpoint, endpoint_from_html_head)

    def test_get_endpoint_in_html_body(self):
        """Endpoints exposed in HTML <body> are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(),
            text=snippets.html_body_endpoint(),
        )
        endpoint_from_html_body = outgoing_webmentions._get_endpoint_in_html(
            mock_response
        )
        self.assertEqual(self.relative_endpoint, endpoint_from_html_body)

    def test_relative_to_absolute_url(self):
        """Relative URLs are correctly converted to absolute URLs."""

        domain = settings.DOMAIN_NAME
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

    def test_find_links_in_text(self):
        """Outgoing links are found correctly."""

        urls = {
            f"https://{testfunc.random_domain()}",
            f"http://{testfunc.random_domain()}/some-path",
            f"{testfunc.random_domain()}/some-path/something_else_04/",
            f"https://subdomain.{testfunc.random_domain()}/blah-blah/",
        }

        outgoing_content = "".join(
            [
                f'This is some content that mentions <a href="{url}">this page</a>'
                for url in urls
            ]
        )

        outgoing_links = outgoing_webmentions._find_links_in_text(outgoing_content)
        self.assertSetEqual(outgoing_links, urls)

    def test_find_links_in_text__should_remove_duplicates(self):
        outgoing_links = outgoing_webmentions._find_links_in_text(
            OUTGOING_WEBMENTION_HTML_DUPLICATE_LINKS
        )

        self.assertSetEqual(
            {"https://beatonma.org/", "https://snommoc.org/"}, outgoing_links
        )


class OutgoingWebmentionsTests(WebmentionTestCase):
    source_url = f"https://{settings.DOMAIN_NAME}/some-url-path/"

    @_patch_post(ok=True)
    def test_send_webmention(self):
        """_send_webmention should return True with status code when webmention is accepted by server."""

        success, status_code = outgoing_webmentions._send_webmention(
            source_url=self.source_url,
            endpoint=f"https://{TARGET_DOMAIN}/webmention/",
            target=f"https://{TARGET_DOMAIN}/",
        )

        self.assertTrue(success)
        self.assertEqual(200, status_code)

    @_patch_post(ok=False)
    def test_send_webmention__with_endpoint_error(self):
        """_send_webmention should return False with status code when webmention is not accepted by server."""

        success, status_code = outgoing_webmentions._send_webmention(
            source_url=self.source_url,
            endpoint=f"https://{TARGET_DOMAIN}/webmention/",
            target=f"https://{TARGET_DOMAIN}/",
        )

        self.assertFalse(success)
        self.assertEqual(400, status_code)

    @_patch_post(ok=True)
    @_patch_get(ok=True)
    def test_process_outgoing_webmentions(self):
        """Test the entire process_outgoing_webmentions task with no errors."""
        self.assertEqual(0, OutgoingWebmentionStatus.objects.count())

        successful_submissions = process_outgoing_webmentions(
            self.source_url, OUTGOING_WEBMENTION_HTML
        )

        self.assertEqual(1, successful_submissions)
        self.assertEqual(1, OutgoingWebmentionStatus.objects.count())

        successful_submissions = process_outgoing_webmentions(
            self.source_url, OUTGOING_WEBMENTION_HTML_MULTIPLE_LINKS
        )

        self.assertEqual(2, successful_submissions)
        self.assertEqual(3, OutgoingWebmentionStatus.objects.count())

    # No network requests should be made if links not found in text
    @patch.object(requests, "get", None)
    @patch.object(requests, "post", None)
    def test_process_outgoing_webmentions__with_no_links_found(self):
        """Test the entire process_outgoing_webmentions task with no links in provided text."""
        self.assertEqual(0, OutgoingWebmentionStatus.objects.count())

        successful_webmention_submissions = process_outgoing_webmentions(
            self.source_url, OUTGOING_WEBMENTION_HTML_NO_LINKS
        )

        self.assertEqual(0, successful_webmention_submissions)
        self.assertEqual(0, OutgoingWebmentionStatus.objects.count())

    @_patch_get(ok=True)
    @_patch_post(ok=False)
    def test_process_outgoing_webmentions__with_endpoint_error(self):
        """Test the entire process_outgoing_webmentions task with endpoint error."""

        successful_webmention_submissions = process_outgoing_webmentions(
            self.source_url, OUTGOING_WEBMENTION_HTML
        )

        self.assertEqual(0, successful_webmention_submissions)
        self.assertEqual(1, OutgoingWebmentionStatus.objects.count())
