"""
Tests for handling webmentions are sent to us from elsewhere.
"""

import logging

from django.http import HttpResponse
from django.test import Client

from mentions.tasks import incoming_webmentions
from mentions.util import split_url
from tests import WebmentionTestCase
from tests.util import testfunc

log = logging.getLogger(__name__)


class _MockHttpClient:
    """Wrap Django Client with API for `python-requests`."""

    def __init__(self, client: Client):
        self.django_client = client

    def get(self, url):
        return _MockResponse(self.django_client.get(url))


class _MockResponse:
    """Wrap Django HttpResponse with API for `python-requests`."""

    def __init__(self, response: HttpResponse):
        self.response = response
        self.headers = response.headers
        self.status_code = response.status_code
        self.text = response.content


class IncomingWebmentionsTests(WebmentionTestCase):
    def setUp(self):
        target_pk, self.target_slug = testfunc.get_id_and_slug()

        self.target = testfunc.create_mentionable_object()
        self.target_url = testfunc.get_url_for_slug(self.target.slug)

    def test_get_target_path(self):
        """Ensure that path is retrieved from url correctly."""
        scheme, domain, path = split_url(self.target_url)
        self.assertEqual(self.target.get_absolute_url(), path)

    def test_get_target_object(self):
        """Ensure that database object is retrieved from url correctly."""
        retrieved_model = incoming_webmentions._get_target_object(self.target_url)

        self.assertEqual(retrieved_model.slug, self.target.slug)

    def test_get_incoming_source(self):
        """Ensure that webmention source page can be retrieved correctly."""
        source_url = testfunc.create_mentionable_object().get_absolute_url()

        self.assertIsNotNone(
            incoming_webmentions._get_incoming_source_text(
                source_url, client=_MockHttpClient(self.client)
            )
        )
