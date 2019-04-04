from django.urls import re_path

from .views import GetWebmentionsView, WebmentionView, names as view_names

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
    re_path(
        r'^$',
        WebmentionView.as_view(),
        name=view_names.webmention_api_incoming),
    re_path(
        r'^get/?$',
        GetWebmentionsView.as_view(),
        name=view_names.webmention_api_get_for_object),
]
