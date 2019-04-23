"""Constants that are used in several separate tests."""
from django.conf import settings

domain = settings.DOMAIN_NAME if hasattr(settings, 'DOMAIN_NAME') else 'localhost'
namespace = (settings.WEBMENTION_NAMESPACE
             if hasattr(settings, 'WEBMENTION_NAMESPACE')
             else 'webmention')

webmention_api_absolute_url = f'{domain}/{namespace}/'
webmention_api_relative_url = f'/{namespace}/'
webmention_api_get_relative_url = f'/{namespace}/get/'

"""Dotted name of the model used for testing."""
model_name = 'tests.MentionableTestModel'

"""Name of the View used for testing (for reverse lookup)"""
view_all_endpoints = 'all_endpoints_view'

"""Path as configured in the local urlpatterns"""
correct_config = 'with_correct_config'

"""Regular expression for the slug used in urlpatterns."""
slug_regex = r'(?P<slug>[\w\-.]+)/?$'
