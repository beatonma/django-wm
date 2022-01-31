from django.urls import include, path, re_path

from mentions.tests.util import constants, viewname
from mentions.tests.views import AllEndpointsMentionableTestView, SimpleNoObjectTestView

urlpatterns = [
    # A page associated with a MentionableMixin model with correct configuration - webmentions linked by model instance.
    re_path(
        fr"^{constants.correct_config}/{constants.slug_regex}",
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
