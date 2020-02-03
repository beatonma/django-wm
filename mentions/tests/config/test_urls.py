from django.urls import path, include, re_path

from mentions.tests.util import constants
from mentions.tests.views import (
    AllEndpointsMentionableTestView,
    SimpleNoObjectTestView,
)

urlpatterns = [
    re_path(
        fr'^{constants.namespace}/{constants.correct_config}/{constants.slug_regex}',
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            'model_name': constants.model_name,
        },
        name=constants.view_all_endpoints),
    path(f'{constants.namespace}/', include('mentions.urls')),
    path('some-page/', SimpleNoObjectTestView.as_view(), name=constants.view_no_mentionable_object)
]
