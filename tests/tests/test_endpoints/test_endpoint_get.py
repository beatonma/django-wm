"""
Make sure we can correctly retrieve Webmentions for a given url/object.
"""

import logging
from typing import Dict, List

from mentions.models import Webmention
from tests.tests.util import testfunc
from tests.tests.util.testcase import WebmentionTestCase

log = logging.getLogger(__name__)


def get_mention_of_type(mentions, _type: str):
    return next(filter(lambda x: x["type"] == _type, mentions))


class _BaseTestCase(WebmentionTestCase):
    """ENDPOINT: /get tests"""

    endpoint = testfunc.endpoint_get_webmentions()

    def get_json_response(
        self,
        url: str,
        expected_status: int = 200,
        expected_count: int = 2,
    ) -> List[Dict]:
        response = self.get_endpoint_mentions(url)

        self.assertEqual(response.status_code, expected_status)

        mentions = response.json()["mentions"]
        self.assertEqual(expected_count, len(mentions))
        return mentions


class GetWebmentionsForModelTests(_BaseTestCase):
    """ENDPOINT `/get`: Retrieve mentions associated with a MentionableMixin object."""

    def setUp(self):
        self.target_object = testfunc.create_mentionable_object()
        self.webmention_source_url = testfunc.random_url()
        self.simplemention_source_url = testfunc.random_url()

        testfunc.create_webmention(
            source_url=self.webmention_source_url,
            target_object=self.target_object,
        )

        testfunc.create_simple_mention(
            source_url=self.simplemention_source_url,
            target_object=self.target_object,
        )

    def test_webmentions_retrieved_correctly(self):
        """Webmentions that target an object are retrieved correctly."""
        mentions = self.get_json_response(
            url=self.target_object.get_absolute_url(),
        )

        webmention = get_mention_of_type(mentions, "webmention")
        self.assertEqual(webmention["source_url"], self.webmention_source_url)
        self.assertEqual(webmention["type"], "webmention")

    def test_simplementions_retrieved_correctly(self):
        """SimpleMentions that target an object are retrieved correctly."""
        mentions = self.get_json_response(url=self.target_object.get_absolute_url())

        simple = get_mention_of_type(mentions, "simple")
        self.assertEqual(simple["source_url"], self.simplemention_source_url)
        self.assertEqual(simple["type"], "simple")


class GetWebmentionsNoModelTests(_BaseTestCase):
    """ENDPOINT `/get`: Retrieve mentions associated with URL."""

    def setUp(self):
        self.target_url = testfunc.get_simple_url()
        self.webmention_source_url = testfunc.random_url()
        self.simplemention_source_url = testfunc.random_url()

        testfunc.create_webmention(
            source_url=self.webmention_source_url,
            target_url=self.target_url,
        )
        testfunc.create_simple_mention(
            source_url=self.simplemention_source_url,
            target_url=self.target_url,
        )

    def test_webmentions_retrieved_correctly(self):
        """Webmentions that target a URL are retrieved correctly."""
        mentions = self.get_json_response(url=self.target_url)

        webmention = get_mention_of_type(mentions, "webmention")
        self.assertEqual(webmention["source_url"], self.webmention_source_url)

    def test_webmention_type_retrieved_correctly(self):
        """Webmention with post_type is serialized correctly."""
        wm = self.assert_exists(Webmention)
        wm.post_type = "bookmark"
        wm.save(update_fields=["post_type"])

        mentions = self.get_json_response(url=self.target_url)

        serialized_wm = get_mention_of_type(mentions, "bookmark")
        self.assertIsNotNone(serialized_wm)

    def test_simplementions_retrieved_correctly(self):
        """SimpleMentions that target a URL are retrieved correctly."""
        mentions = self.get_json_response(url=self.target_url)

        simple = get_mention_of_type(mentions, "simple")
        self.assertEqual(simple["source_url"], self.simplemention_source_url)
        self.assertEqual(simple["type"], "simple")


class GetWebmentionsBadRequestTests(_BaseTestCase):
    """ENDPOINT `/get`: Poorly-formed requests should give suitable responses."""

    def test_get_webmentions_view__require_http_get(self):
        """HTTP POST/PATCH/DELETE gives 405 error code."""
        response = self.client.post(self.endpoint)
        self.assertEqual(405, response.status_code)

        response = self.client.patch(self.endpoint)
        self.assertEqual(405, response.status_code)

        response = self.client.delete(self.endpoint)
        self.assertEqual(405, response.status_code)

    def test_get_webmentions_view__require_param_for_url(self):
        """Missing query parameter `url` gives 400 error code."""
        response = self.client.get(self.endpoint)
        self.assertEqual(400, response.status_code)

    def test_get_webmentions_view__target_does_not_exist(self):
        """Unresolvable `url` parameter return 404 error code with empty mentions list."""
        self.get_json_response(
            url="/does-not-exist",
            expected_status=404,
            expected_count=0,
        )
