from mentions.tasks.incoming.reverify import reverify_mention
from tests.tests.util import testfunc
from tests.tests.util.mocking import patch_http_get, patch_http_post
from tests.tests.util.testcase import WebmentionTestCase


class ReverifyMentionTests(WebmentionTestCase):
    def setUp(self):
        super().setUp()
        self.target_url = testfunc.get_simple_url()
        self.source_url = testfunc.random_url()


class PositiveTests(ReverifyMentionTests):
    """Tests that result in a mention being marked as valid."""

    def setUp(self):
        super().setUp()

        self.mention = testfunc.create_webmention(
            source_url=self.source_url,
            target_url=self.target_url,
            validated=False,
            notes="Sample",
        )

    def test_reverify_invalid_webmention(self):
        self.mention = testfunc.create_webmention(
            source_url=self.source_url,
            target_url=self.target_url,
            validated=False,
            notes="Sample",
        )

        with patch_http_get(
            text=f"""<a href="{self.target_url}">link</a>"""
        ), patch_http_post():
            reverify_mention(self.mention)

        self.mention.refresh_from_db()
        self.assertTrue(self.mention.validated)
        self.assertIn("Sample\n", self.mention.notes)
        self.assertIn("Updated fields:", self.mention.notes)


class NegativeTests(ReverifyMentionTests):
    """Tests that result in a mention being marked as invalid."""

    def setUp(self):
        super().setUp()
        self.mention = testfunc.create_webmention(
            source_url=self.source_url,
            target_url=self.target_url,
            validated=True,
            notes="Sample",
        )

    def test_reverify_valid_webmention(self):
        with patch_http_get(status_code=400), patch_http_post():
            reverify_mention(self.mention)

        self.mention.refresh_from_db()
        self.assertFalse(self.mention.validated)

    def test_reverify_webmention(self):
        with patch_http_get(), patch_http_post():
            reverify_mention(self.mention)

        self.mention.refresh_from_db()
        self.assertFalse(self.mention.validated)
