"""
Tests for handling webmentions are sent to us from elsewhere.
"""
import logging
from unittest.mock import Mock, patch

import requests

from mentions.exceptions import SourceNotAccessible, TargetWrongDomain
from mentions.models import Webmention
from mentions.models.mixins import IncomingMentionType
from mentions.tasks import incoming
from mentions.tasks.incoming import local, remote
from mentions.util import html_parser
from tests import MockResponse, WebmentionTestCase
from tests.util import snippets, testfunc

log = logging.getLogger(__name__)


SOURCE_URL_OK = testfunc.random_url()
SOURCE_URL_NOT_FOUND = testfunc.random_url()
SOURCE_URL_UNSUPPORTED_CONTENT_TYPE = testfunc.random_url()
SOURCE_URL_NO_MENTIONS = testfunc.random_url()

TARGET_URL = testfunc.get_simple_url(absolute=True)
SOURCE_TEXT = f"""<div>
<a href="{TARGET_URL}" class="u-repost-of">link to target url</a>
<div class="h-card">
    <a class="u-url" href="https://janebloggs.org">Jane</a>
</div>
"""

SOURCE_TEXT_WITH_REPOST = f"""<div>
<a href="{TARGET_URL}" class="u-repost-of">link to target url</a>
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

SOURCE_TEXT_LIKE = f"""<a href="{TARGET_URL}" class="u-like-of another-class"></a><"""
SOURCE_TEXT_REPLY_IN_HCITE = f"""<div class="h-entry">
    <div class="h-cite u-in-reply-to">
        Liked <a class="u-url" href="{TARGET_URL}">a post</a> by
        <span class="p-author h-card">
             <a class="u-url p-name" href="https://example.com">Author Name</a>
        </span>:
        <blockquote class="e-content">
            <p>The post being liked</p>
        </blockquote>
    </div>
</div>"""


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
        Mock(side_effect=lambda x, **kw: _mock_get_text(x, **kwargs, **kw)),
    )


class IncomingWebmentionsTests(WebmentionTestCase):
    """INCOMING: Tests for task `process_incoming_webmention`."""

    def setUp(self):
        self.target = testfunc.create_mentionable_object()
        self.target_url = testfunc.get_absolute_url_for_object(self.target)

    def test_get_target_object(self):
        """Target object is resolved from URL correctly."""
        retrieved_model = local.get_target_object(self.target_url)

        self.assertEqual(retrieved_model.slug, self.target.slug)

    def test_get_target_object_wrong_domain_raises_exception(self):
        """Target URL with wrong domain raises TargetWrongDomain."""
        with self.assertRaises(TargetWrongDomain):
            local.get_target_object(testfunc.random_url())

    @_patch_get()
    def test_get_incoming_source(self):
        """Incoming source text is retrieved correctly."""
        text = remote.get_source_html(SOURCE_URL_OK)
        self.assertTrue(SOURCE_TEXT in text)

    @_patch_get()
    def test_get_incoming_source_inaccessible_url(self):
        """Inaccessible source URL raises SourceNotAccessible."""
        with self.assertRaises(SourceNotAccessible):
            remote.get_source_html(SOURCE_URL_NOT_FOUND)

    @_patch_get()
    def test_get_incoming_source_unsupported_content_type(self):
        """Source URL with unsupported content type raises SourceNotAccessible."""
        with self.assertRaises(SourceNotAccessible):
            remote.get_source_html(SOURCE_URL_UNSUPPORTED_CONTENT_TYPE)

    def test_process_incoming_webmention(self):
        """process_incoming_webmention targeting a URL creates a validated Webmention object when successful."""
        with _patch_get():
            incoming.process_incoming_webmention(
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

    def test_process_incoming_webmention_with_post_type(self):
        with _patch_get(text=SOURCE_TEXT_WITH_REPOST):
            incoming.process_incoming_webmention(
                source_url=SOURCE_URL_OK,
                target_url=TARGET_URL,
                sent_by=testfunc.random_url(),
            )

        mention: Webmention = Webmention.objects.first()
        self.assertEqual(mention.source_url, SOURCE_URL_OK)
        self.assertEqual(mention.target_url, TARGET_URL)
        self.assertTrue(mention.validated)

        hcard = mention.hcard
        self.assertIsNotNone(hcard)
        self.assertEqual(hcard.name, "Jane")

        self.assertEqual(mention.post_type, "repost")

    def test_process_incoming_webmention_with_target_object(self):
        """process_incoming_webmention targeting an object creates a validated Webmention object when successful."""

        with _patch_get(text=SOURCE_TEXT_FOR_OBJECT.format(url=self.target_url)):
            incoming.process_incoming_webmention(
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
            incoming.process_incoming_webmention(
                source_url=SOURCE_URL_NO_MENTIONS,
                target_url=TARGET_URL,
                sent_by=testfunc.random_url(),
            )

        webmentions = Webmention.objects.all()
        self.assertEqual(1, webmentions.count())

        mention = webmentions.first()
        self.assertFalse(mention.validated)

    def test_parse_link_type(self):
        soup = html_parser(SOURCE_TEXT_LIKE)
        link = soup.find("a", href=TARGET_URL)

        link_type = remote.parse_post_type(link)
        self.assertEqual(link_type, IncomingMentionType.Like)

    def test_parse_link_type_with_hcite_nesting(self):
        soup = html_parser(SOURCE_TEXT_REPLY_IN_HCITE)
        link = soup.find("a", href=TARGET_URL)

        link_type = remote.parse_post_type(link)
        self.assertEqual(link_type, IncomingMentionType.Reply)
