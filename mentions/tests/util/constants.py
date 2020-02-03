"""Constants that are used in several separate tests."""
from django.conf import settings
from django.urls import reverse_lazy
import mentions.views.names as view_names

domain = settings.DOMAIN_NAME
namespace = 'webmention'

webmention_api_relative_url = reverse_lazy(view_names.webmention_api_incoming)
webmention_api_get_relative_url = reverse_lazy(
    view_names.webmention_api_get_for_object)

"""Value updated after django initation by runtests.py"""
webmention_api_absolute_url = ''

"""Dotted name of the model used for testing."""
model_name = 'tests.MentionableTestModel'

"""Name of the View used for testing (for reverse lookup)"""
view_all_endpoints = 'all_endpoints_view'
view_no_mentionable_object = 'no_object_view'

"""Path as configured in the local urlpatterns"""
correct_config = 'with_correct_config'

"""Regular expression for the slug used in urlpatterns."""
slug_regex = r'(?P<slug>[\w\-.]+)/?$'
