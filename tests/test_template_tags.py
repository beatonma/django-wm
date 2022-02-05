from django.urls import reverse

from mentions.tasks import outgoing_webmentions
from tests import WebmentionTestCase
from tests.util import testfunc


class TemplateTagTests(WebmentionTestCase):
    """TEMPLATE: Test template tags."""

    def test_webmention_endpoint_templatetag(self):
        """{% webmention_endpoint %} renders correctly."""
        expected_endpoint = testfunc.endpoint_submit_webmention()
        response = self.client.get(reverse("test-template-tags"))

        self.assertTemplateUsed(response, "templatetags_example.html")
        self.assertContains(response, expected_endpoint)

        self.assertEqual(
            outgoing_webmentions._get_endpoint_in_html(response.content),
            expected_endpoint,
        )
