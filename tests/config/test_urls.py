from django.contrib import admin
from django.urls import include, path

from mentions.helpers.urls import mentions_path
from tests.models import HelperMentionableTestModel
from tests.util import constants, viewname
from tests.views import (
    AllEndpointsMentionableTestView,
    HelperMentionableTestView,
    MiddlewareView,
    SimpleNoObjectTestView,
    TemplateTagTestView,
)

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
    # Same as above, using mentions_path helper.
    mentions_path(
        "with_helper_config/<int:arbitrary_name>/",
        HelperMentionableTestView.as_view(),
        model_class=HelperMentionableTestModel,
        model_field_mapping={"arbitrary_name": "id"},
        name=viewname.helper_with_target_object_view,
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
    path(
        "middleware/",
        MiddlewareView.as_view(),
        name=viewname.middleware,
    ),
    path(f"{constants.namespace}/", include("mentions.urls")),
    path("test-admin/", admin.site.urls),
]
