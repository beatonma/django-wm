import logging

from django.apps import AppConfig

log = logging.getLogger(__name__)


class SampleAppConfig(AppConfig):
    name = "sample_app"
