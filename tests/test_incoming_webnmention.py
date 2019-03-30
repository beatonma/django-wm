"""
Tests for handling webmentions are sent to us from elsewhere.
"""

import logging

from django.http import HttpResponse
from django.test import TestCase, Client
from django.urls import reverse

from mentions.tasks import incoming_webmentions
from mentions.tests import util
from mentions.tests.models import MentionableTestModel
from mentions.tests.util import constants
from mentions.tests.util.urls import urlpatterns as correct_urlpatterns
from mentions.urls import urlpatterns

log = logging.getLogger(__name__)

HTML_MENTION = '''
<html>
<head>
</head>
<body><a href="{target_url}">This mentions the target!</a></body>
</html>
'''

urlpatterns += correct_urlpatterns


def build_object_url(slug):
    return f'{constants.domain}{reverse(constants.view_all_endpoints, args=[slug])}'


class MockHttpClient:
    """Wrap Django Client with API for `python-requests`."""

    def __init__(self, client: Client):
        self.django_client = client

    def get(self, url):
        return MockResponse(self.django_client.get(url))


class MockResponse:
    """Wrap Django HttpResponse with API for `python-requests`."""

    def __init__(self, response: HttpResponse):
        self.response = response
        self.headers = {
            'content-type': response._content_type_for_repr,
        }
        self.status_code = response.status_code
        self.text = response.content


class IncomingWebmentionsTests(TestCase):

    def setUp(self):
        self.target_id, self.target_slug = util.get_id_and_slug()
        self.target_url = build_object_url(self.target_slug)

        target = MentionableTestModel.objects.create(
            stub_id=self.target_id,
            slug=self.target_slug,
            content='some html content',
            allow_incoming_webmentions=True)
        target.save()

    def test_get_target_object(self):
        """Ensure that database object is retrieved from url correctly."""
        log.debug(self.target_url)

        retrieved_model = incoming_webmentions._get_target_object(self.target_url)

        self.assertEqual(retrieved_model.slug, self.target_slug)

    def test_get_incoming_source(self):
        """Ensure that webmention source page can be retrieved correctly."""

        source_stub_id, source_slug = util.get_id_and_slug()
        source = MentionableTestModel.objects.create(
            stub_id=source_stub_id,
            slug=source_slug,
            content=HTML_MENTION.format(target_url=self.target_url))
        source.save()
        source_url = build_object_url(source_slug)

        self.assertIsNotNone(
            incoming_webmentions._get_incoming_source(
                source_url, client=MockHttpClient(self.client)))
