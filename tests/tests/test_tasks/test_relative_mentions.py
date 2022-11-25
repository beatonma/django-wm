from django.urls import reverse

from mentions import config
from mentions.models import OutgoingWebmentionStatus, Webmention
from mentions.tasks.incoming import process_incoming_webmention
from mentions.tasks.outgoing import process_outgoing_webmentions
from tests.test_app.models import MentionableTestModel
from tests.tests.util import snippets, testfunc, viewname
from tests.tests.util.mocking import patch_http_get, patch_http_post
from tests.tests.util.testcase import OptionsTestCase

RECEIVER_ID = 1
SENDER_ID = 2

RECEIVER_URLPATH = reverse(viewname.with_target_object_view, args=[RECEIVER_ID])
RECEIVER_ABSOLUTE_URL = config.build_url(RECEIVER_URLPATH)

SENDER_URLPATH = reverse(viewname.with_target_object_view, args=[SENDER_ID])
SENDER_ABSOLUTE_URL = config.build_url(SENDER_URLPATH)

RECEIVER_CONTENT = snippets.html_all_endpoints("Some interesting content")
SENDER_CONTENT = snippets.build_html(
    body=f"""<p>
        This content mentions
        <a href="{RECEIVER_URLPATH}">
            webmention_receiver
        </a>
        with a relative url path.
    </p>
    """
)


class RelativeUrlMentionTests(OptionsTestCase):
    """Ensure that relative URL mentions are sent and validated correctly."""

    def setUp(self) -> None:
        super().setUp()
        self.receiver = MentionableTestModel.objects.create(
            id=RECEIVER_ID,
            content=RECEIVER_CONTENT,
        )

        self.sender = MentionableTestModel.objects.create(
            id=SENDER_ID,
            content=SENDER_CONTENT,
        )

    @patch_http_post()
    @patch_http_get(text=RECEIVER_CONTENT)
    def test_submit_relative_webmention(self):
        successful = process_outgoing_webmentions(
            self.sender.get_absolute_url(),
            self.sender.get_content_html(),
        )

        self.assertEqual(1, successful)

        outgoing = OutgoingWebmentionStatus.objects.get(
            target_url=RECEIVER_ABSOLUTE_URL,
            source_url=SENDER_URLPATH,
        )
        self.assertTrue(outgoing.successful)

    @patch_http_get(text=SENDER_CONTENT)
    def test_receive_relative_webmention(self):
        process_incoming_webmention(
            source_url=SENDER_ABSOLUTE_URL,
            target_url=RECEIVER_ABSOLUTE_URL,
            sent_by=testfunc.random_url(),
        )

        received = Webmention.objects.get(
            target_url=RECEIVER_ABSOLUTE_URL, source_url=SENDER_ABSOLUTE_URL
        )
        self.assertTrue(received.validated)
