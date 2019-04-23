from django.urls import path, re_path

import mentions.views.names as view_names
from mentions.views.webmention import GetWebmentionsView, WebmentionView

"""
/webmention/
Configure in django.conf.settings.WEBMENTION_NAMESPACE and root project urls.py
e.g.
    from django.conf import settings
    urlpatterns = [
        ...,
        re_path(fr'{settings.WEBMENTION_NAMESPACE}/', include('mentions.urls')),
        ...,
    ]
"""
urlpatterns = [
    path(
        '',
        WebmentionView.as_view(),
        name=view_names.webmention_api_incoming),
    re_path(
        r'^get/?$',
        GetWebmentionsView.as_view(),
        name=view_names.webmention_api_get_for_object),
]
