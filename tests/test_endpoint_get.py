"""
Make sure we can correctly retrieve Webmentions for a given url/object.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple

from mentions.models import SimpleMention, Webmention
from tests import WebmentionTestCase
from tests.util import testfunc

log = logging.getLogger(__name__)


class _BaseTestCase(WebmentionTestCase):
    """ENDPOINT: /get tests"""

    endpoint = testfunc.endpoint_get_webmentions()

    def get_json_response(
        self, url, data=None, **kwargs
    ) -> Tuple[int, Optional[List[Dict]]]:
        response = self.client.get(url, data=data, **kwargs)
        return response.status_code, json.loads(response.content).get("mentions")


class GetWebmentionsForModelTests(_BaseTestCase):
    """ENDPOINT `/get`: Retrieve mentions associated with a MentionableMixin object."""

    def setUp(self):
        self.target_object = testfunc.create_mentionable_object()
        self.webmention_source_url = testfunc.random_url()
        self.simplemention_source_url = testfunc.random_url()

        Webmention.objects.create(
            source_url=self.webmention_source_url,
            target_object=self.target_object,
            validated=True,
            approved=True,
        )

        SimpleMention.objects.create(
            source_url=self.simplemention_source_url,
            target_object=self.target_object,
        )

    def test_webmentions_retrieved_correctly(self):
        """Webmentions that target an object are retrieved correctly."""
        status, mentions = self.get_json_response(
            self.endpoint, data={"url": self.target_object.get_absolute_url()}
        )

        self.assertEqual(status, 200)
        self.assertEqual(len(mentions), 2)

        webmention = next(filter(lambda x: x["type"] == "webmention", mentions))
        self.assertEqual(webmention["source_url"], self.webmention_source_url)
        self.assertEqual(webmention["type"], "webmention")

    def test_simplementions_retrieved_correctly(self):
        """SimpleMentions that target an object are retrieved correctly."""
        status, mentions = self.get_json_response(
            self.endpoint, data={"url": self.target_object.get_absolute_url()}
        )

        self.assertEqual(status, 200)
        self.assertEqual(len(mentions), 2)

        simple = next(filter(lambda x: x["type"] == "simple", mentions))
        self.assertEqual(simple["source_url"], self.simplemention_source_url)
        self.assertEqual(simple["type"], "simple")


class GetWebmentionsNoModelTests(_BaseTestCase):
    """ENDPOINT `/get`: Retrieve mentions associated with URL."""

    def setUp(self):
        self.target_url = testfunc.get_simple_url()
        self.webmention_source_url = testfunc.random_url()
        self.simplemention_source_url = testfunc.random_url()

        Webmention.objects.create(
            source_url=self.webmention_source_url,
            target_url=self.target_url,
            validated=True,
            approved=True,
        )

        SimpleMention.objects.create(
            source_url=self.simplemention_source_url,
            target_url=self.target_url,
        )

    def test_webmentions_retrieved_correctly(self):
        """Webmentions that target a URL are retrieved correctly."""
        status, mentions = self.get_json_response(
            self.endpoint, data={"url": self.target_url}
        )

        self.assertEqual(status, 200)
        self.assertEqual(len(mentions), 2)

        webmention = next(filter(lambda x: x["type"] == "webmention", mentions))
        self.assertEqual(webmention["source_url"], self.webmention_source_url)
        self.assertEqual(webmention["type"], "webmention")

    def test_simpleentions_retrieved_correctly(self):
        """SimpleMentions that target a URL are retrieved correctly."""
        status, mentions = self.get_json_response(
            self.endpoint, data={"url": self.target_url}
        )

        self.assertEqual(status, 200)
        self.assertEqual(len(mentions), 2)

        simple = next(filter(lambda x: x["type"] == "simple", mentions))
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
        status, mentions = self.get_json_response(
            self.endpoint,
            data={"url": "/does-not-exist"},
        )

        self.assertEqual(status, 404)
        self.assertListEqual([], mentions)
