from django.urls import include, path

from tests.util import constants, viewname
from tests.views import (
    AllEndpointsMentionableTestView,
    SimpleNoObjectTestView,
    TemplateTagTestView,
)

urlpatterns = [
    # A page associated with a MentionableMixin model with correct configuration - webmentions linked by model instance.
    path(
        fr"with_correct_config/<slug:slug>",
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            "model_name": constants.model_name,
        },
        name=viewname.with_target_object_view,
    ),
    # An arbitrary page with no model association - webmentions are linked by URL.
    path(
        "some-page/",
        SimpleNoObjectTestView.as_view(),
        name=viewname.no_object_view,
    ),
    path(
        "templatetagstest",
        TemplateTagTestView.as_view(),
        name="test-template-tags",
    ),
    path(f"{constants.namespace}/", include("mentions.urls")),
]
