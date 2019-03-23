"""Stuff needed by more than one test file."""
from django.urls import re_path

# from .views.mentionable import MentionableTestView
from .views.mentionable import (
    AllEndpointsMentionableTestView,
    HttpHeaderMentionableTestView,
    HtmlAnchorMentionableTestView,
    HtmlRelLinkMentionableTestView,
    UnmentionableTestView,
)
from . import constants

correct_urlpatterns = [
    re_path(
        fr'^{constants.correct_config}/(?P<slug>[\w\-.]+)/?$',
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            'model_name': constants.model_name,
        },
        name=constants.all_endpoints_view),
    re_path(
        fr'^{constants.correct_config}/(?P<slug>[\w\-.]+)/?$',
        HttpHeaderMentionableTestView.as_view(),
        kwargs={
            'model_name': constants.model_name,
        },
        name=constants.http_header_view),
    re_path(
        fr'^{constants.correct_config}/(?P<slug>[\w\-.]+)/?$',
        HtmlAnchorMentionableTestView.as_view(),
        kwargs={
            'model_name': constants.model_name,
        },
        name=constants.html_anchor_view),
    re_path(
        fr'^{constants.correct_config}/(?P<slug>[\w\-.]+)/?$',
        HtmlRelLinkMentionableTestView.as_view(),
        kwargs={
            'model_name': constants.model_name,
        },
        name=constants.html_head_view),
    re_path(
        fr'^{constants.correct_config}/(?P<slug>[\w\-.]+)/?$',
        UnmentionableTestView.as_view(),
        kwargs={
            'model_name': constants.model_name,
        },
        name=constants.http_header_view),
]


def url(path, slug=''):
    return f'/{constants.namespace}/{path}/{slug}'
