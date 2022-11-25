from mentions.models.mixins import IncomingMentionType
from tests.tests.util import testfunc
from tests.tests.util.testcase import WebmentionTestCase


class GetMentionsByTypeEndpointTests(WebmentionTestCase):
    def test_endpoint_get_by_type(self):
        obj = testfunc.create_mentionable_object()
        testfunc.create_webmention(
            target_object=obj,
            post_type=IncomingMentionType.Repost,
            quote="hello",
        )
        for _ in range(2):
            testfunc.create_webmention(
                target_object=obj,
                post_type=IncomingMentionType.Like,
            )

        testfunc.create_webmention(target_object=obj)

        response = self.get_endpoint_mentions_by_type(obj.get_absolute_url())

        data = response.json()["mentions_by_type"]
        self.assertEqual(
            data["repost"][0]["quote"],
            "hello",
        )

        self.assertEqual(2, len(data["like"]))
        self.assertEqual(1, len(data["webmention"]))

    def test_endpoint_get_by_type_404(self):
        obj = testfunc.create_mentionable_object()
        url = obj.get_absolute_url()
        obj.delete()

        response = self.get_endpoint_mentions_by_type(url)
        self.assertEqual(404, response.status_code)
