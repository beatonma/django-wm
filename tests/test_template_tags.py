from django.urls import reverse

from mentions.tasks.outgoing import remote
from tests import WebmentionTestCase
from tests.util import testfunc


class TemplateTagTests(WebmentionTestCase):
    """TEMPLATE: Test template tags."""

    def test_webmention_endpoint_templatetag(self):
        """{% webmentions_endpoint %} renders correctly."""
        expected_endpoint = testfunc.endpoint_submit_webmention()
        response = self.client.get(reverse("test-template-tags"))

        self.assertTemplateUsed(response, "templatetags_example.html")
        self.assertContains(response, expected_endpoint)

        self.assertEqual(
            remote.get_endpoint_in_html(response.content),
            expected_endpoint,
        )
