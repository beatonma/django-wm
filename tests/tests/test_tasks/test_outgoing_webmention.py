"""
Tests for webmentions that originate on our server, usually pointing somewhere else.
"""
import logging

from mentions import config
from mentions.models import OutgoingWebmentionStatus
from mentions.tasks import handle_pending_webmentions
from mentions.tasks.outgoing import process_outgoing_webmentions, remote
from tests.tests.util import testfunc
from tests.tests.util.mocking import patch_http_get, patch_http_post
from tests.tests.util.testcase import OptionsTestCase

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


class OutgoingWebmentionsTests(OptionsTestCase):
    """OUTOOING: tests for task `process_outgoing_webmentions`."""

    source_url = config.build_url("/some-url-path/")

    @patch_http_post()
    def test_send_webmention(self):
        """_send_webmention should return True with status code when webmention is accepted by server."""

        success, status_code = remote._send_webmention(
            source_urlpath=self.source_url,
            endpoint=f"https://{TARGET_DOMAIN}/webmention/",
            target=f"https://{TARGET_DOMAIN}/",
        )

        self.assertTrue(success)
        self.assertEqual(200, status_code)

    @patch_http_post(status_code=400)
    def test_send_webmention__with_endpoint_error(self):
        """_send_webmention should return False with status code when webmention is not accepted by server."""

        success, status_code = remote._send_webmention(
            source_urlpath=self.source_url,
            endpoint=f"https://{TARGET_DOMAIN}/webmention/",
            target=f"https://{TARGET_DOMAIN}/",
        )

        self.assertFalse(success)
        self.assertEqual(400, status_code)

    @patch_http_post()
    @patch_http_get(text=OUTGOING_WEBMENTION_HTML)
    def test_process_outgoing_webmentions(self):
        """Test the entire process_outgoing_webmentions task with no errors."""
        successful = process_outgoing_webmentions(
            self.source_url, OUTGOING_WEBMENTION_HTML
        )

        self.assertEqual(1, successful)
        self.assert_exists(OutgoingWebmentionStatus)

        successful = process_outgoing_webmentions(
            self.source_url, OUTGOING_WEBMENTION_HTML_MULTIPLE_LINKS
        )

        self.assertEqual(2, successful)
        self.assert_exists(OutgoingWebmentionStatus, count=2)

    @patch_http_get()
    @patch_http_post()
    def test_process_outgoing_webmentions__with_no_links_found(self):
        """Test the entire process_outgoing_webmentions task with no links in provided text."""
        successful = process_outgoing_webmentions(
            self.source_url, OUTGOING_WEBMENTION_HTML_NO_LINKS
        )

        self.assertEqual(0, successful)
        self.assert_not_exists(OutgoingWebmentionStatus)

    @patch_http_get()
    @patch_http_post(status_code=400)
    def test_process_outgoing_webmentions__with_endpoint_error(self):
        """Test the entire process_outgoing_webmentions task with endpoint error."""

        successful = process_outgoing_webmentions(
            self.source_url, OUTGOING_WEBMENTION_HTML
        )

        self.assertEqual(0, successful)
        self.assert_exists(OutgoingWebmentionStatus)

    @patch_http_get(text=OUTGOING_WEBMENTION_HTML)
    @patch_http_post(status_code=400)
    def test_process_outgoing_webmentions__recycles_status(self):
        self.enable_celery(False)
        self.set_retry_interval(0)

        # Process links from text to target url.
        process_outgoing_webmentions(self.source_url, OUTGOING_WEBMENTION_HTML)
        status = self.assert_exists(OutgoingWebmentionStatus)
        self.assertEqual(status.retry_attempt_count, 1)

        # After failure, retrying process increments retry_attempt_count.
        handle_pending_webmentions()
        status.refresh_from_db()
        self.assertEqual(status.retry_attempt_count, 2)

        # Reprocessing raw text reuses same status instance, resetting its retry tracking.
        process_outgoing_webmentions(self.source_url, OUTGOING_WEBMENTION_HTML)

        status = self.assert_exists(OutgoingWebmentionStatus)
        self.assertEqual(status.retry_attempt_count, 1)
