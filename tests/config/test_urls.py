from django.urls import include, path, re_path

from tests.util import constants, viewname
from tests.views import AllEndpointsMentionableTestView, SimpleNoObjectTestView

urlpatterns = [
    # A page associated with a MentionableMixin model with correct configuration - webmentions linked by model instance.
    path(
        fr"with_correct_config/<slug:slug>",
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            "model_name": constants.model_name,
        },
        name=viewname.with_all_endpoints,
    ),
    # An arbitrary page with no model association - webmentions are linked by URL.
    path(
        "some-page/",
        SimpleNoObjectTestView.as_view(),
        name=viewname.with_no_mentionable_object,
    ),
    path(f"{constants.namespace}/", include("mentions.urls")),
]
