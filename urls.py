from django.urls import re_path

from .views import GetWebmentionsView, WebmentionView

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
        name='webmention_view'),
    re_path(
        r'^get/?$',
        GetWebmentionsView.as_view(),
        name='get_webmentions_view'),
]
