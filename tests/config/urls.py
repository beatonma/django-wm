from django.urls import include, path

from tests.test_app.views import AllEndpointsMentionableTestView, SimpleNoObjectTestView
from tests.tests.util import constants, testfunc, viewname

# Patterns that we almost always want to include.
core_urlpatterns = [
    # An arbitrary page with no model association - webmentions are linked by URL.
    path(
        testfunc.random_str(),
        SimpleNoObjectTestView.as_view(),
        name=viewname.no_object_view,
    ),
    path(f"{constants.namespace}/", include("mentions.urls")),
]


# Default patterns which we sometimes want to disable/override.
urlpatterns = [
    # A page associated with a MentionableMixin model with correct configuration - webmentions linked by model instance.
    path(
        "with_correct_config/<int:object_id>",
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            "model_name": constants.model_name,
        },
        name=viewname.with_target_object_view,
    ),
    *core_urlpatterns,
]
