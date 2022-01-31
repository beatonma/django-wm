"""
Make sure we can correctly retrieve Webmentions for a given url/object.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple

from django.urls import reverse

from mentions.models import Webmention
from mentions.tests import WebmentionTestCase
from mentions.tests.models import MentionableTestModel
from mentions.tests.util import constants, testfunc, viewname

log = logging.getLogger(__name__)


class MentionsForObjectTestCase(WebmentionTestCase):
    def get_json_response(
        self, url, data=None, **kwargs
    ) -> Tuple[int, Optional[List[Dict]]]:
        response = self.client.get(url, data=data, **kwargs)
        return response.status_code, json.loads(response.content).get("mentions")


class WebmentionGetTests(MentionsForObjectTestCase):
    """`get/` endpoint: Well-formed requests return mentions associated with URL"""

    def setUp(self):
        target_pk, target_slug = testfunc.get_id_and_slug()

        target = MentionableTestModel.objects.create(
            pk=target_pk,
            slug=target_slug,
            allow_incoming_webmentions=True,
        )
        self.target_url = reverse(viewname.with_all_endpoints, args=[target_slug])

        source_pk, source_slug = testfunc.get_id_and_slug()
        source = MentionableTestModel.objects.create(
            pk=source_pk,
            slug=source_slug,
            content=testfunc.get_mentioning_content(self.target_url),
        )
        self.source_url = testfunc.build_object_url(source_slug)

        Webmention.objects.create(
            source_url=testfunc.build_object_url(source.slug),
            target_url=testfunc.build_object_url(target.slug),
            sent_by="tests@localhost",
            validated=True,
            approved=True,
            target_object=target,
        )

    def test_get_webmentions_view__with_valid_object(self):
        """Ensure that we can correctly retrieve webmentions for a given url."""
        status, mentions = self.get_json_response(
            constants.webmention_api_get_relative_url, data={"url": self.target_url}
        )

        self.assertEqual(status, 200)
        self.assertEqual(len(mentions), 1)

        first_mention = mentions[0]
        self.assertEqual(first_mention["source_url"], self.source_url)


class WebmentionGetBadRequestTests(MentionsForObjectTestCase):
    """`get/` endpoint: Poorly-formed requests should give suitable responses"""

    def test_get_webmentions_view__require_http_get(self):
        """get/ endpoint does not accept HTTP POST/PATCH/DELETE."""
        response = self.client.post(constants.webmention_api_get_relative_url)
        self.assertEqual(405, response.status_code)

        response = self.client.patch(constants.webmention_api_get_relative_url)
        self.assertEqual(405, response.status_code)

        response = self.client.delete(constants.webmention_api_get_relative_url)
        self.assertEqual(405, response.status_code)

    def test_get_webmentions_view__require_param_for_url(self):
        """Missing query parameter `url` gives 400 error code."""
        response = self.client.get(constants.webmention_api_get_relative_url)
        self.assertEqual(400, response.status_code)

    def test_get_webmentions_view__target_does_not_exist(self):
        """If target URL does not exist, return 404 error code with empty mentions list."""
        status, mentions = self.get_json_response(
            constants.webmention_api_get_relative_url,
            data={"url": "/does-not-exist"},
        )

        self.assertEqual(status, 404)
        self.assertListEqual([], mentions)


class WebmentionNoModelTests(MentionsForObjectTestCase):
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
            constants.webmention_api_get_relative_url,
            data={"url": self.target_url},
        )

        self.assertEqual(status, 200)
        self.assertEqual(len(mentions), 1)

        first_mention = mentions[0]
        self.assertEqual(first_mention["source_url"], "https://beatonma.org/")
