from tests import WebmentionTestCase
from tests.models import MentionableTestModel
from tests.util import testfunc


class MentionsEndpointsTests(WebmentionTestCase):
    """Make sure endpoints actually work."""

    def test_incoming_endpoint(self):
        response = self.client.get(testfunc.endpoint_submit_webmention())
        self.assertEqual(200, response.status_code)

    def test_get_endpoint(self):
        _, slug = testfunc.get_id_and_slug()
        obj = MentionableTestModel.objects.create(slug=slug)

        response = self.client.get(
            testfunc.endpoint_get_webmentions(), data={"url": obj.get_absolute_url()}
        )
        self.assertEqual(200, response.status_code)
