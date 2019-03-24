"""
Tests for webmentions that originate on our server, usually pointing
somewhere else.
"""
import logging
from dataclasses import dataclass, field

from django.test import TestCase
from django.urls import reverse

import uuid

from django.utils.text import slugify

from mentions.tests import util
from mentions.tests.util import constants
from mentions.tests.util.constants import endpoints
from mentions.tests.util.constants import view_names
from mentions.tests.models import MentionableTestModel

from mentions.tasks import outgoing_webmentions

log = logging.getLogger(__name__)

HTTP_LINK_ENDPOINT = endpoints.http_header_link(endpoints.webmention_api_relative_url)
HTML_HEAD_ENDPOINT = f'''
<html>
<head>
    {endpoints.html_head_link(endpoints.webmention_api_relative_url)}
</head>
<body></body>
</html>
'''
HTML_BODY_ENDPOINT = f'''
<html>
<head></head>
<body>
    {endpoints.html_body_link(endpoints.webmention_api_relative_url)}
</body>
</html>
'''


def _get_mentioning_content(url):
    """Return html content that links to the given url."""
    return f'''
        This is some content that mentions the target <a href="{url}">url</a>
    '''


def _get_id_and_slug():
    """Create a random id and slug for a MentionableTestModel."""
    _id = uuid.uuid4().hex[:6]
    slug = slugify(_id)
    return _id, slug


@dataclass
class MockResponse:
    url: str
    text: str = None
    headers: dict = field(default_factory=dict)


class OutgoingWebmentionsTests(TestCase):

    def setUp(self):
        self.target_stub_id, self.target_slug = _get_id_and_slug()

        target = MentionableTestModel.objects.create(
            stub_id=self.target_stub_id,
            slug=self.target_slug,
            allow_incoming_webmentions=True)
        target.save()

    def _get_target_url(self, viewname):
        return reverse(viewname, args=[self.target_slug])

    def _get_absolute_target_url(self, viewname):
        return f'{constants.domain}{self._get_target_url(viewname)}'

    def test_find_links_in_text(self):
        """Ensure that outgoing links are found correctly."""

        outgoing_content = _get_mentioning_content(
            reverse(view_names.all_endpoints, args=[self.target_slug]))

        outgoing_links = outgoing_webmentions._find_links_in_text(outgoing_content)
        self.assertEqual(
            outgoing_links,
            [util.url(constants.correct_config,
                      view_names.all_endpoints,
                      self.target_slug)])

    def test_get_absolute_endpoint_from_response(self):
        """Ensure that any exposed endpoints are found and returned as an absolute url."""
        mock_response = MockResponse(
            url=self._get_absolute_target_url(view_names.all_endpoints),
            headers={'Link': HTTP_LINK_ENDPOINT})
        absolute_endpoint_from_http_headers = outgoing_webmentions._get_absolute_endpoint_from_response(
            mock_response)
        self.assertEqual(endpoints.webmention_api_absolute_url, absolute_endpoint_from_http_headers)

        mock_response.headers = {}
        mock_response.text = HTML_HEAD_ENDPOINT
        absolute_endpoint_from_html_head = outgoing_webmentions._get_absolute_endpoint_from_response(
            mock_response)
        self.assertEqual(endpoints.webmention_api_absolute_url, absolute_endpoint_from_html_head)

        mock_response.headers = {}
        mock_response.text = HTML_BODY_ENDPOINT
        absolute_endpoint_from_html_body = outgoing_webmentions._get_absolute_endpoint_from_response(
            mock_response)
        self.assertEqual(endpoints.webmention_api_absolute_url, absolute_endpoint_from_html_body)

    def test_get_endpoint_in_http_headers(self):
        """Ensure that endpoints exposed in http header are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(view_names.all_endpoints),
            headers={'Link': HTTP_LINK_ENDPOINT})
        endpoint_from_http_headers = outgoing_webmentions._get_endpoint_in_http_headers(
            mock_response)
        self.assertEqual(endpoints.webmention_api_relative_url, endpoint_from_http_headers)

    def test_get_endpoint_in_html_head(self):
        """Ensure that endpoints exposed in html <head> are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(view_names.all_endpoints),
            text=HTML_HEAD_ENDPOINT)
        endpoint_from_html_head = outgoing_webmentions._get_endpoint_in_html(mock_response)
        self.assertEqual(endpoints.webmention_api_relative_url, endpoint_from_html_head)

    def test_get_endpoint_in_html_body(self):
        """Ensure that endpoints exposed in html <body> are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(view_names.all_endpoints),
            text=HTML_BODY_ENDPOINT)
        endpoint_from_html_body = outgoing_webmentions._get_endpoint_in_html(mock_response)
        self.assertEqual(endpoints.webmention_api_relative_url, endpoint_from_html_body)

    def test_relative_to_absolute_url(self):
        """Ensure that relative urls are correctly converted to absolute"""

        domain = constants.domain
        page_url = f'{domain}/some-url-path'
        response = MockResponse(url=page_url)

        absolute_url_from_root = outgoing_webmentions._relative_to_absolute_url(
            response, '/webmention')
        self.assertEqual(f'{domain}/webmention', absolute_url_from_root)

        absolute_url_from_relative = outgoing_webmentions._relative_to_absolute_url(
            response, 'webmention')
        self.assertEqual(f'{domain}/webmention', absolute_url_from_relative)

        already_absolute_url = outgoing_webmentions._relative_to_absolute_url(
            response, f'{domain}/already_absolute_path')
        self.assertEqual(f'{domain}/already_absolute_path',
                         already_absolute_url)

    # def test_send_webmention(self):
    #     outgoing_stub_id, outgoing_slug = _get_id_and_slug()
    #
    #     outgoing = MentionableTestModel.objects.create(
    #         stub_id=outgoing_stub_id,
    #         slug=outgoing_slug)
    #     outgoing.save()
    #
    #     source_url = reverse(view_names.all_endpoints, args=[outgoing_slug])
    #     endpoint = endpoints.webmention_api_absolute_url
    #     target_url = self._get_absolute_target_url(view_names.all_endpoints)
    #
    #     success = outgoing_webmentions._send_webmention(
    #         source_url=source_url, endpoint=endpoint, target=target_url)
    #     self.assertTrue(success)
