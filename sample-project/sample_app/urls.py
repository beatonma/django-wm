from django.urls import include, path
from sample_app.models import Blog
from sample_app.views.actions import ActionView
from sample_app.views.content import ArticleView, BlogView
from sample_app.views.unreliable import MaybeTimeoutView, TimeoutView

from mentions.helpers.urls import mentions_path

urlpatterns = [
    mentions_path(
        "blog/<int:blog_id>/",
        BlogView.as_view(),
        model_class=Blog,
        model_filter_map={
            "blog_id": "id",
        },
        name="blog",
    ),
    path(
        "article/<int:article_id>/",
        ArticleView.as_view(),
        name="article",
        kwargs={
            "model_name": "sample_app.Article",
        },
    ),
    path("timeout/", TimeoutView.as_view(), name="timeout"),
    path("unreliable/", MaybeTimeoutView.as_view(), name="unreliable"),
    path("", ActionView.as_view(), name="actions"),
]
