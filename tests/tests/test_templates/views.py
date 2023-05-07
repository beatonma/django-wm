from django.urls import path
from django.views.generic import TemplateView

from tests.config.urls import core_urlpatterns

TEMPLATE_TEST_VIEW_NAME = "test-template-tags-view"


class TemplateTagTestView(TemplateView):
    """Render page to test `{% webmentions_endpoint %}` tag."""

    template_name = "templatetags_example.html"


urlpatterns = core_urlpatterns + [
    path(
        "templatetagstest/",
        TemplateTagTestView.as_view(),
        name=TEMPLATE_TEST_VIEW_NAME,
    ),
]
