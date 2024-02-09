"""
Tests for handling webmentions are sent to us from elsewhere.
"""
import logging

from django.test import override_settings

from mentions import options
from mentions.exceptions import SourceNotAccessible, TargetWrongDomain
from mentions.models import Webmention
from mentions.models.mixins import IncomingMentionType
from mentions.tasks import incoming
from mentions.tasks.incoming import local, remote
from mentions.util import html_parser
from tests.tests.util import snippets, testfunc
from tests.tests.util.mocking import patch_http_get
from tests.tests.util.testcase import (
    OptionsTestCase,
    SimpleTestCase,
    WebmentionTestCase,
)

log = logging.getLogger(__name__)


SOURCE_URL = testfunc.random_url()
TARGET_URL = testfunc.get_simple_url()

SOURCE_TEXT_DEFAULT = f"""<div>
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


class IncomingWebmentionsTests(WebmentionTestCase):
    """INCOMING: Tests for task `process_incoming_webmention`."""

    def setUp(self):
        self.target = testfunc.create_mentionable_object()
        self.target_url = testfunc.get_absolute_url_for_object(self.target)

    def test_get_target_object(self):
        """Target object is resolved from URL correctly."""
        retrieved_model = local.get_target_object(self.target_url)

        self.assertEqual(retrieved_model.pk, self.target.pk)

    def test_get_target_object_wrong_domain_raises_exception(self):
        """Target URL with wrong domain raises TargetWrongDomain."""
        with self.assertRaises(TargetWrongDomain):
            local.get_target_object(testfunc.random_url())

    @patch_http_get(text=SOURCE_TEXT_DEFAULT)
    def test_get_incoming_source(self):
        """Incoming source text is retrieved correctly."""
        text = remote.get_source_html(testfunc.random_url())
        self.assertTrue(SOURCE_TEXT_DEFAULT in text)

    @patch_http_get(status_code=404)
    def test_get_incoming_source_inaccessible_url(self):
        """Inaccessible source URL raises SourceNotAccessible."""
        with self.assertRaises(SourceNotAccessible):
            remote.get_source_html(testfunc.random_url())

    @patch_http_get(headers={"content-type": "image/jpeg"})
    def test_get_incoming_source_unsupported_content_type(self):
        """Source URL with unsupported content type raises SourceNotAccessible."""
        with self.assertRaises(SourceNotAccessible):
            remote.get_source_html(testfunc.random_url())

    @patch_http_get(text=SOURCE_TEXT_DEFAULT)
    def test_process_incoming_webmention(self):
        """process_incoming_webmention targeting a URL creates a validated Webmention object when successful."""
        incoming.process_incoming_webmention(
            source_url=SOURCE_URL,
            target_url=TARGET_URL,
            sent_by=testfunc.random_url(),
        )

        mention = self.assert_exists(Webmention)
        self.assertEqual(mention.source_url, SOURCE_URL)
        self.assertEqual(mention.target_url, TARGET_URL)
        self.assertTrue(mention.validated)

        hcard = mention.hcard
        self.assertIsNotNone(hcard)
        self.assertEqual(hcard.name, "Jane")

    @patch_http_get(text=SOURCE_TEXT_WITH_REPOST)
    def test_process_incoming_webmention_with_post_type(self):
        incoming.process_incoming_webmention(
            source_url=SOURCE_URL,
            target_url=TARGET_URL,
            sent_by=testfunc.random_url(),
        )

        mention = self.assert_exists(Webmention)
        self.assertEqual(mention.source_url, SOURCE_URL)
        self.assertEqual(mention.target_url, TARGET_URL)
        self.assertTrue(mention.validated)

        hcard = mention.hcard
        self.assertIsNotNone(hcard)
        self.assertEqual(hcard.name, "Jane")

        self.assertEqual(mention.post_type, "repost")

    def test_process_incoming_webmention_with_target_object(self):
        """process_incoming_webmention targeting an object creates a validated Webmention object when successful."""

        with patch_http_get(text=SOURCE_TEXT_FOR_OBJECT.format(url=self.target_url)):
            incoming.process_incoming_webmention(
                source_url=SOURCE_URL,
                target_url=self.target_url,
                sent_by=testfunc.random_url(),
            )

        mention = self.assert_exists(Webmention)
        self.assertEqual(mention.source_url, SOURCE_URL)
        self.assertEqual(mention.target_url, self.target_url)
        self.assertTrue(mention.validated)

        hcard = mention.hcard
        self.assertIsNotNone(hcard)
        self.assertEqual(hcard.name, "Jane")

    @patch_http_get(text=snippets.build_html(body=SOURCE_TEXT_NO_MENTION))
    def test_process_incoming_webmention_no_mentions_in_source(self):
        """process_incoming_webmention creates unvalidated Webmention object when target link not found in source text."""
        incoming.process_incoming_webmention(
            source_url=SOURCE_URL,
            target_url=TARGET_URL,
            sent_by=testfunc.random_url(),
        )

        mention = self.assert_exists(Webmention)
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


class IncomingWebmentionOptionTests(OptionsTestCase):
    """INCOMING: Test effects of settings.WEBMENTIONS_TARGET_REQUIRES_OBJECT."""

    def assert_webmention_count(
        self,
        expected_count: int,
        text: str = SOURCE_TEXT_DEFAULT,
        target_url: str = TARGET_URL,
    ) -> Webmention:
        with patch_http_get(text=text):
            incoming.process_incoming_webmention(
                source_url=SOURCE_URL,
                target_url=target_url,
                sent_by=testfunc.random_url(),
            )

        return self.assert_exists(Webmention, count=expected_count)

    def test_process_incoming_webmention_with_object_not_required(self):
        """When mention does not target a model instance, setting False accepts the mention."""
        self.set_incoming_target_model_required(False)

        mention = self.assert_webmention_count(1)
        self.assertIsNone(mention.target_object)

    def test_process_incoming_webmention_with_object_required(self):
        """When mention does not target a model instance, setting True ignores the mention."""
        self.set_incoming_target_model_required(True)

        self.assert_webmention_count(0)

    def test_target_object_with_object_required(self):
        """When mention targets a model instance, setting has no effect."""
        self.set_incoming_target_model_required(True)

        target_obj = testfunc.create_mentionable_object()
        target_url = testfunc.get_absolute_url_for_object(target_obj)

        mention = self.assert_webmention_count(
            1,
            text=SOURCE_TEXT_FOR_OBJECT.format(url=target_url),
            target_url=target_url,
        )
        self.assertIsNotNone(mention.target_object)

    def test_target_object_with_object_not_required(self):
        """When mention targets a model instance, setting has no effect."""
        self.set_incoming_target_model_required(False)

        target_obj = testfunc.create_mentionable_object()
        target_url = testfunc.get_absolute_url_for_object(target_obj)

        mention = self.assert_webmention_count(
            1,
            text=SOURCE_TEXT_FOR_OBJECT.format(url=target_url),
            target_url=target_url,
        )
        self.assertIsNotNone(mention.target_object)


class AllowDenyOptionTests(SimpleTestCase):
    @override_settings(**{options.SETTING_DOMAINS_INCOMING_ALLOW: {"allow.org"}})
    @patch_http_get(text=SOURCE_TEXT_DEFAULT)
    def test_process_incoming_webmention_with_domains_allow(self):
        self.assertIsNotNone(
            incoming.process_incoming_webmention(
                testfunc.random_url(subdomain="", domain="allow.org", port=""),
                TARGET_URL,
                sent_by=testfunc.random_url(),
            )
        )
        self.assertIsNone(
            incoming.process_incoming_webmention(
                testfunc.random_url(subdomain="", domain="other.org", port=""),
                TARGET_URL,
                sent_by=testfunc.random_url(),
            )
        )

    @override_settings(**{options.SETTING_DOMAINS_INCOMING_DENY: {"deny.org"}})
    @patch_http_get(text=SOURCE_TEXT_DEFAULT)
    def test_process_incoming_webmention_with_domains_deny(self):
        self.assertIsNotNone(
            incoming.process_incoming_webmention(
                testfunc.random_url(subdomain="", domain="allow.org", port=""),
                TARGET_URL,
                sent_by=testfunc.random_url(),
            )
        )
        self.assertIsNone(
            incoming.process_incoming_webmention(
                testfunc.random_url(subdomain="", domain="deny.org", port=""),
                TARGET_URL,
                sent_by=testfunc.random_url(),
            )
        )
