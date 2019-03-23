"""Stuff needed by more than one test file."""
from django.urls import re_path

from .views.mentionable import MentionableTestStubView

# Base URL path (global urlpatterns)
namespace = 'webmention'

# Path as configured in the local urlpatterns
correct_config = 'with_correct_config'

correct_urlpatterns = [
    re_path(
        fr'^{correct_config}/(?P<slug>[\w\-.]+)/?$',
        MentionableTestStubView.as_view(),
        kwargs={
            'model_name': 'tests.MentionableTestStub',
        },
        name='mentionable_test_stub_view'),
]


def url(path, slug=''):
    return f'/{namespace}/{path}/{slug}'
