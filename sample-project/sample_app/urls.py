from django.urls import path
from sample_app.views import ActionView, ArticleView

urlpatterns = [
    path(
        "article/<int:article_id>/",
        ArticleView.as_view(),
        name="article",
        kwargs={
            "model_name": "sample_app.Article",
        },
    ),
    path("", ActionView.as_view(), name="actions"),
]
