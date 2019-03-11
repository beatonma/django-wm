import logging

from django.conf import settings
from django.test import TestCase

from django.urls import re_path

from mentions.util import get_model_for_url
from mentions.views import GetWebmentionsView, WebmentionView

from mentions.models.test import MentionableTestStub
from mentions.urls import urlpatterns
from mentions.views.test import MentionableTestStubView

log = logging.getLogger(__name__)

urlpatterns += [
    re_path(
        r'^mentionable_test_stub/(?P<slug>[\w\-.]+)/?$',
        MentionableTestStubView.as_view(),
        kwargs={
            'model_name': 'mentions.MentionableTestStub',
        },
        name='mentionable_test_stub_view'),
]


class WebmentionTasksTestCase(TestCase):
    def setUp(self):
        self.stub_id = 'some-id123'
        self.slug = 'some-slug'

        MentionableTestStub.objects.create(
            stub_id=self.stub_id,
            slug=self.slug).save()

    def test_get_model_for_url(self):
        '''Ensure that reverse url lookup finds the correct object.'''
        retreived_object = get_model_for_url(
            f'/webmention/mentionable_test_stub/{self.slug}')
        log.info(f'model: {retreived_object}')

        self.assertEqual(retreived_object.stub_id, self.stub_id)
