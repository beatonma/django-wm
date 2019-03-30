from django.urls import re_path

from mentions.tests.views import AllEndpointsMentionableTestView
from . import constants

urlpatterns = [
    re_path(
        fr'^{constants.correct_config}/{constants.slug_regex}',
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            'model_name': constants.model_name,
        },
        name=constants.view_all_endpoints),
]
