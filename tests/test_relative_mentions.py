from django.urls import reverse

from mentions import config
from mentions.models import OutgoingWebmentionStatus, Webmention
from mentions.tasks.incoming import process_incoming_webmention
from mentions.tasks.outgoing import process_outgoing_webmentions
from tests import OptionsTestCase, patch_http_get, patch_http_post
from tests.models import MentionableTestModel
from tests.util import snippets, testfunc, viewname

RECEIVER_SLUG = "webmention_receiver"
SENDER_SLUG = "webmention_sender"

RECEIVER_URLPATH = reverse(viewname.with_target_object_view, args=[RECEIVER_SLUG])
RECEIVER_ABSOLUTE_URL = config.build_url(RECEIVER_URLPATH)

SENDER_URLPATH = reverse(viewname.with_target_object_view, args=[SENDER_SLUG])
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
            content=RECEIVER_CONTENT,
            slug=RECEIVER_SLUG,
        )

        self.sender = MentionableTestModel.objects.create(
            content=SENDER_CONTENT,
            slug=SENDER_SLUG,
        )

    @patch_http_post()
    @patch_http_get(text=RECEIVER_CONTENT)
    def test_submit_relative_webmention(self):
        successful = process_outgoing_webmentions(
            self.sender.get_absolute_url(),
            self.sender.all_text(),
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
