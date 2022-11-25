from mentions.models import HCard
from mentions.models.mixins import IncomingMentionType
from mentions.tasks.incoming.remote import get_metadata_from_source
from tests.tests.util import testfunc
from tests.tests.util.testcase import WebmentionTestCase


class PostTypeTests(WebmentionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.target_url = testfunc.get_absolute_url_for_object()
        self.source_url = testfunc.random_url()

    def test_post_type_parsed_from_hcite_parent(self):
        html = f"""
            This article is a response to <span class="h-cite u-in-reply-to">
                <a href="{self.target_url}"> this post</a> by <span class="h-card">YourName</span>.
            </span>"""

        data = get_metadata_from_source(html, self.target_url, self.source_url)
        self.assertEqual(data.post_type, IncomingMentionType.Reply.serialized_name())

        # `h-card` is present but it belongs to the `h-cite` so is not the document author.
        self.assert_not_exists(HCard)

    def test_post_type_parsed_from_link(self):
        html = f"""This article is a response to <a class="u-translation-of" href="{self.target_url}">this post</a>"""
        data = get_metadata_from_source(html, self.target_url, self.source_url)
        self.assertEqual(
            data.post_type, IncomingMentionType.Translation.serialized_name()
        )
        self.assert_not_exists(HCard)
