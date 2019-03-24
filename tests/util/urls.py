from django.urls import re_path

# from .views.mentionable import MentionableTestView
from mentions.tests.views.mentionable import (
    AllEndpointsMentionableTestView,
    HttpHeaderMentionableTestView,
    HtmlAnchorMentionableTestView,
    HtmlRelLinkMentionableTestView,
    UnmentionableTestView,
)
from mentions.tests.util import constants
from mentions.tests.util.constants import view_names

correct_urlpatterns = [
    re_path(
        fr'^{constants.correct_config}/{view_names.all_endpoints}/'
        fr'{constants.slug_regex}',
        AllEndpointsMentionableTestView.as_view(),
        kwargs={
            'model_name': constants.model_name,
        },
        name=view_names.all_endpoints),
    re_path(
        fr'^{constants.correct_config}/{view_names.http_header}/'
        fr'{constants.slug_regex}',
        HttpHeaderMentionableTestView.as_view(),
        kwargs={
            'model_name': constants.model_name,
        },
        name=view_names.http_header),
    re_path(
        fr'^{constants.correct_config}/{view_names.html_anchor}/'
        fr'{constants.slug_regex}',
        HtmlAnchorMentionableTestView.as_view(),
        kwargs={
            'model_name': constants.model_name,
        },
        name=view_names.html_anchor),
    re_path(
        fr'^{constants.correct_config}/{view_names.html_head}/'
        fr'{constants.slug_regex}',
        HtmlRelLinkMentionableTestView.as_view(),
        kwargs={
            'model_name': constants.model_name,
        },
        name=view_names.html_head),
    re_path(
        fr'^{constants.correct_config}/{view_names.unmentionable}/'
        fr'{constants.slug_regex}',
        UnmentionableTestView.as_view(),
        kwargs={
            'model_name': constants.model_name,
        },
        name=view_names.unmentionable),
]


def url(path, view, slug=''):
    return f'/{constants.namespace}/{path}/{view}/{slug}'
