from django.urls import re_path

from .views import GetWebmentionsView, WebmentionView

# /webmention/
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
