import logging

from django.apps import AppConfig

log = logging.getLogger(__name__)


class SampleAppWagtailConfig(AppConfig):
    name = "sample_app_wagtail"
