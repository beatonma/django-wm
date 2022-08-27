from django.urls import path
from sample_app.views import ActionView, ArticleView, MaybeTimeoutView, TimeoutView

urlpatterns = [
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
