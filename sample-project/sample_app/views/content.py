from django.shortcuts import render
from sample_app.models import Article, Blog
from sample_app.views import BaseView, default_context


class ArticleView(BaseView):
    def get(self, request, article_id: int, *args, **kwargs):
        article = Article.objects.get(pk=article_id)
        return render(
            request,
            "sample_app/article.html",
            context={
                **default_context,
                "article": article,
            },
        )


class BlogView(BaseView):
    def get(self, request, blog_id: int, *args, **kwargs):
        blog = Blog.objects.get(pk=blog_id)
        return render(
            request,
            "sample_app/article.html",
            context={
                **default_context,
                "article": blog,
            },
        )
