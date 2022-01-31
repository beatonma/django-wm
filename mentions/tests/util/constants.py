"""Constants that are used in several tests."""
from django.conf import settings
from django.urls import reverse_lazy

import mentions.views.view_names as view_names

domain = settings.DOMAIN_NAME

"""The root path for mentions.urls"""
namespace = "webmention"

webmention_api_relative_url = reverse_lazy(view_names.webmention_api_incoming)
webmention_api_get_relative_url = reverse_lazy(view_names.webmention_api_get_for_object)

"""Value updated after django initiation by runtests.py"""
webmention_api_absolute_url = None

"""Dotted name of the model used for testing."""
model_name = "tests.MentionableTestModel"

"""Path as configured in the local urlpatterns"""
correct_config = "with_correct_config"

"""Regular expression for the slug used in urlpatterns."""
slug_regex = r"(?P<slug>[\w\-.]+)/?$"
