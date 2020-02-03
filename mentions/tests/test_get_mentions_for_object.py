"""
Make sure we can correctly retrieve Webmentions for a given url/object.
"""

import json
import logging

from django.test import TestCase
from django.urls import reverse

from mentions.models import Webmention
from mentions.tests.models import MentionableTestModel
from mentions.tests.util import functions
from mentions.tests.util import constants

log = logging.getLogger(__name__)


def _create_quick_webmention(source, target, valid=True, approved=True):
    wm = Webmention.create(
        functions.build_object_url(source.slug),
        functions.build_object_url(target.slug),
        sent_by='tests@localhost')
    wm.validated = valid
    wm.approved = approved
    wm.target_object = target
    wm.save()


class WebmentionGetTests(TestCase):
    """"""
    def setUp(self):
        self.target_stub_id, self.target_slug = functions.get_id_and_slug()

        target = MentionableTestModel.objects.create(
            stub_id=self.target_stub_id,
            slug=self.target_slug,
            allow_incoming_webmentions=True)
        target.save()
        self.target_url = functions.build_object_relative_url(self.target_slug)

        self.source_stub_id, self.source_slug = functions.get_id_and_slug()
        source = MentionableTestModel.objects.create(
            stub_id=self.source_stub_id,
            slug=self.source_slug,
            content=functions.get_mentioning_content(self.target_url))
        source.save()
        self.source_url = functions.build_object_url(self.source_slug)

        _create_quick_webmention(source, target)

    def test_get_webmentions_view__with_valid_object(self):
        """Ensure that we can correctly retrieve webmentions for a given url."""
        response = self.client.get(
            constants.webmention_api_get_relative_url,
            data={'url': self.target_url})

        json_response = json.loads(response.content)
        log.info(json_response)
        self.assertEqual(json_response['status'], 1)

        _mentions = json_response['mentions']
        self.assertEqual(len(_mentions), 1)

        first_mention = _mentions[0]
        self.assertEqual(first_mention['source_url'], self.source_url)


class WebmentionGetBadRequestTests(TestCase):
    """"""
    def test_get_webmentions_view__require_http_get(self):
        """Ensure that webmentions get view does not accept HTTP POST."""
        response = self.client.post(constants.webmention_api_get_relative_url)
        self.assertEqual(405, response.status_code)

    def test_get_webmentions_view__require_param_for_url(self):
        response = self.client.get(constants.webmention_api_get_relative_url)
        self.assertEqual(400, response.status_code)

    def test_get_webmentions_view__target_does_not_exist(self):
        response = self.client.get(
            constants.webmention_api_get_relative_url,
            data={'url': '/does-not-exist'})

        json_response = json.loads(response.content)
        self.assertEqual(json_response['status'], 0)



class WebmentionNoModelTests(TestCase):
    """"""
    def setUp(self) -> None:
        self.target_url = reverse(constants.view_no_mentionable_object)
        Webmention.objects.create(
            source_url='https://django-wm.dev/',
            target_url=self.target_url,
            approved=True,
            validated=True,
        ).save()

    def test_get_webmentions_view__no_mentionable_model(self):
        response = self.client.get(
            constants.webmention_api_get_relative_url,
            data={'url': self.target_url})

        json_response = json.loads(response.content)
        print(json_response)

        _mentions = json_response['mentions']
        self.assertEqual(len(_mentions), 1)

        first_mention = _mentions[0]
        self.assertEqual(first_mention['source_url'], 'https://django-wm.dev/')
