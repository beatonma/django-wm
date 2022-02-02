from django.urls import path, re_path

from mentions.views import view_names
from mentions.views.webmention import GetWebmentionsView, WebmentionView
from tests.views import TemplateTagTestView

"""
/webmention/
Configure in root project urls.py
e.g.
    from django.conf import settings
    urlpatterns = [
        ...,
        path(r'webmention/', include('mentions.urls')),
    ]
"""
urlpatterns = [
    path("", WebmentionView.as_view(), name=view_names.webmention_api_incoming),
    re_path(
        r"^get/?$",
        GetWebmentionsView.as_view(),
        name=view_names.webmention_api_get_for_object,
    ),
    path(
        "templatetagstest",
        TemplateTagTestView.as_view(),
        name="test-template-tags",
    ),
]
