"""
Make sure we can correctly retrieve Webmentions for a given url/object.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple

from django.urls import reverse

from mentions.models import Webmention
from tests import WebmentionTestCase
from tests.models import MentionableTestModel
from tests.util import testfunc, viewname

log = logging.getLogger(__name__)


class _MentionsForObjectTestCase(WebmentionTestCase):
    """Tests for `/get` endpoint"""

    endpoint = testfunc.endpoint_get_webmentions()

    def get_json_response(
        self, url, data=None, **kwargs
    ) -> Tuple[int, Optional[List[Dict]]]:
        response = self.client.get(url, data=data, **kwargs)
        return response.status_code, json.loads(response.content).get("mentions")


class WebmentionGetTests(_MentionsForObjectTestCase):
    """Webmention /get endpoint tests"""

    def setUp(self):
        target_pk, target_slug = testfunc.get_id_and_slug()

        target = MentionableTestModel.objects.create(pk=target_pk, slug=target_slug)
        self.target_urlpath = testfunc.get_urlpath(target_slug)

        _, source_slug = testfunc.get_id_and_slug()
        self.source_url = testfunc.get_url(source_slug)

        Webmention.objects.create(
            source_url=testfunc.get_url(source_slug),
            validated=True,
            approved=True,
            target_object=target,
        )

    def test_get_webmentions_view__with_valid_object(self):
        """Correctly resolve webmentions for a MentionableMixin object from a URL."""
        status, mentions = self.get_json_response(
            self.endpoint, data={"url": self.target_urlpath}
        )

        self.assertEqual(status, 200)
        self.assertEqual(len(mentions), 1)

        first_mention = mentions[0]
        self.assertEqual(first_mention["source_url"], self.source_url)


class WebmentionGetBadRequestTests(_MentionsForObjectTestCase):
    """`get/` endpoint: Poorly-formed requests should give suitable responses"""

    def test_get_webmentions_view__require_http_get(self):
        """get/ endpoint does not accept HTTP POST/PATCH/DELETE."""
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
        """If target URL does not exist, return 404 error code with empty mentions list."""
        status, mentions = self.get_json_response(
            self.endpoint,
            data={"url": "/does-not-exist"},
        )

        self.assertEqual(status, 404)
        self.assertListEqual([], mentions)


class WebmentionNoModelTests(_MentionsForObjectTestCase):
    """`get/` endpoint: Pages with no associated model should still be mentionable."""

    def setUp(self) -> None:
        self.target_url = reverse(viewname.with_no_mentionable_object)
        Webmention.objects.create(
            source_url="https://beatonma.org/",
            target_url=self.target_url,
            approved=True,
            validated=True,
        )

    def test_get_webmentions_view__no_mentionable_model(self):
        """Webmentions can be retrieved for a URL even if there is not a MentionableMixin model associated with it."""
        status, mentions = self.get_json_response(
            self.endpoint,
            data={"url": self.target_url},
        )

        self.assertEqual(status, 200)
        self.assertEqual(len(mentions), 1)

        first_mention = mentions[0]
        self.assertEqual(first_mention["source_url"], "https://beatonma.org/")
