import logging

from django.test import TestCase

from main.models import App
from mentions.tasks import webmentions as wm


log = logging.getLogger(__name__)


class WebmentionTasksTestCase(TestCase):
    def setUp(self):
        App.objects.create(
            title='SCII Achievements Manager',
            slug='scii-achievements-manager',
            app_id='sc2am')

    def test_get_model_for_url(self):
        obj = wm._get_model_for_url('app/scii-achievements-manager')
        log.info('model: {}'.format(obj))

        self.assertEqual(obj.title, 'SCII Achievements Manager')
