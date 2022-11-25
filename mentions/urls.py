from django.urls import path, re_path

from mentions.views import view_names
from mentions.views.dashboard import WebmentionDashboardView
from mentions.views.retrieve import GetMentionsByTypeView, GetMentionsView
from mentions.views.submit import WebmentionView

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
        GetMentionsView.as_view(),
        name=view_names.webmention_api_get,
    ),
    re_path(
        r"^get-by-type/?$",
        GetMentionsByTypeView.as_view(),
        name=view_names.webmention_api_get_by_type,
    ),
    path(
        "dashboard/",
        WebmentionDashboardView.as_view(),
        name=view_names.webmention_dashboard,
    ),
]
