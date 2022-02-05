"""
Tests for handling webmentions are sent to us from elsewhere.
"""

import logging
from unittest.mock import Mock, patch

import requests

from mentions.exceptions import SourceNotAccessible, TargetWrongDomain
from mentions.models import Webmention
from mentions.tasks import incoming_webmentions
from tests import MockResponse, WebmentionTestCase
from tests.util import snippets, testfunc

log = logging.getLogger(__name__)


SOURCE_URL_OK = testfunc.random_url()
SOURCE_URL_NOT_FOUND = testfunc.random_url()
SOURCE_URL_UNSUPPORTED_CONTENT_TYPE = testfunc.random_url()
SOURCE_URL_NO_MENTIONS = testfunc.random_url()

TARGET_URL = testfunc.get_simple_url(absolute=True)
SOURCE_TEXT = f"""<div>
<a href="{TARGET_URL}">link to target url</a>
<div class="h-card">
    <a class="u-url" href="https://janebloggs.org">Jane</a>
</div>
"""

SOURCE_TEXT_FOR_OBJECT = """<div>
<a href="{url}">link to target object</a>
<div class="h-card">
    <a class="u-url" href="https://janebloggs.org">Jane</a>
</div>
"""

SOURCE_TEXT_NO_MENTION = f"""<div>
<a href="{testfunc.random_url()}">inaccurate link to target</a>
<div class="h-card">
    <a class="u-url" href="https://janebloggs.org">Jane</a>
</div>
"""


def _response(url, status_code, text, headers=None):
    if headers is None:
        headers = {"content-type": "text/html"}

    return MockResponse(
        url,
        text=text,
        status_code=status_code,
        headers=headers,
    )


def _mock_get_text(url, text=None, **kwargs):
    if text is None:
        text = snippets.build_html(body=SOURCE_TEXT)

    return {
        SOURCE_URL_OK: _response(
            url,
            text=text,
            status_code=200,
        ),
        SOURCE_URL_NOT_FOUND: _response(
            url,
            text=text,
            status_code=404,
        ),
        SOURCE_URL_UNSUPPORTED_CONTENT_TYPE: _response(
            url,
            text=text,
            status_code=200,
            headers={"content-type": "image/jpeg"},
        ),
        SOURCE_URL_NO_MENTIONS: _response(
            url,
            text=text,
            status_code=200,
        ),
    }.get(url)


def _patch_get(**kwargs):
    return patch.object(
        requests,
        "get",
        Mock(side_effect=lambda x: _mock_get_text(x, **kwargs)),
    )


class IncomingWebmentionsTests(WebmentionTestCase):
    """INCOMING: Tests for task `process_incoming_webmention`."""

    def setUp(self):
        self.target = testfunc.create_mentionable_object()
        self.target_url = testfunc.get_absolute_url_for_object(self.target)

    def test_get_target_object(self):
        """Target object is resolved from URL correctly."""
        retrieved_model = incoming_webmentions._get_target_object(self.target_url)

        self.assertEqual(retrieved_model.slug, self.target.slug)

    def test_get_target_object_wrong_domain_raises_exception(self):
        """Target URL with wrong domain raises TargetWrongDomain."""
        with self.assertRaises(TargetWrongDomain):
            incoming_webmentions._get_target_object(testfunc.random_url())

    @_patch_get()
    def test_get_incoming_source(self):
        """Incoming source text is retrieved correctly."""
        text = incoming_webmentions._get_incoming_source_text(SOURCE_URL_OK)
        self.assertTrue(SOURCE_TEXT in text)

    @_patch_get()
    def test_get_incoming_source_inaccessible_url(self):
        """Inaccessible source URL raises SourceNotAccessible."""
        with self.assertRaises(SourceNotAccessible):
            incoming_webmentions._get_incoming_source_text(SOURCE_URL_NOT_FOUND)

    @_patch_get()
    def test_get_incoming_source_unsupported_content_type(self):
        """Source URL with unsupported content type raises SourceNotAccessible."""
        with self.assertRaises(SourceNotAccessible):
            incoming_webmentions._get_incoming_source_text(
                SOURCE_URL_UNSUPPORTED_CONTENT_TYPE
            )

    def test_process_incoming_webmention(self):
        """process_incoming_webmention targeting a URL creates a validated Webmention object when successful."""
        with _patch_get():
            incoming_webmentions.process_incoming_webmention(
                source_url=SOURCE_URL_OK,
                target_url=TARGET_URL,
                sent_by=testfunc.random_url(),
            )

        webmentions = Webmention.objects.all()
        self.assertEqual(1, webmentions.count())

        mention = webmentions.first()
        self.assertEqual(mention.source_url, SOURCE_URL_OK)
        self.assertEqual(mention.target_url, TARGET_URL)
        self.assertTrue(mention.validated)

        hcard = mention.hcard
        self.assertIsNotNone(hcard)
        self.assertEqual(hcard.name, "Jane")

    def test_process_incoming_webmention_with_target_object(self):
        """process_incoming_webmention targeting an object creates a validated Webmention object when successful."""

        with _patch_get(text=SOURCE_TEXT_FOR_OBJECT.format(url=self.target_url)):
            incoming_webmentions.process_incoming_webmention(
                source_url=SOURCE_URL_OK,
                target_url=self.target_url,
                sent_by=testfunc.random_url(),
            )

        webmentions = Webmention.objects.all()
        self.assertEqual(1, webmentions.count())

        mention = webmentions.first()
        self.assertEqual(mention.source_url, SOURCE_URL_OK)
        self.assertEqual(mention.target_url, self.target_url)
        self.assertTrue(mention.validated)

        hcard = mention.hcard
        self.assertIsNotNone(hcard)
        self.assertEqual(hcard.name, "Jane")

    def test_process_incoming_webmention_no_mentions_in_source(self):
        """process_incoming_webmention creates unvalidated Webmention object when target link not found in source text."""

        with _patch_get(text=snippets.build_html(body=SOURCE_TEXT_NO_MENTION)):
            incoming_webmentions.process_incoming_webmention(
                source_url=SOURCE_URL_NO_MENTIONS,
                target_url=TARGET_URL,
                sent_by=testfunc.random_url(),
            )

        webmentions = Webmention.objects.all()
        self.assertEqual(1, webmentions.count())

        mention = webmentions.first()
        self.assertFalse(mention.validated)
