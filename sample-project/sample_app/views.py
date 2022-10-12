import logging
import random
import time

from django import forms
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from sample_app.models import Article, create_article

from mentions import config, options
from mentions.resolution import get_mentions_for_url

log = logging.getLogger(__name__)


default_context = {
    "DOMAIN_NAME": options.domain_name(),
}


class ArticleView(View):
    def get(self, request, article_id: int, *args, **kwargs):
        article = Article.objects.get(pk=article_id)
        return render(
            request,
            "article.html",
            context={
                **default_context,
                "article": article,
            },
        )


class ActionForm(forms.Form):
    target = forms.URLField(required=False)
    author = forms.CharField(required=False, max_length=64)
    type = forms.CharField(
        required=False,
        widget=forms.Select(
            choices=[
                ("", "-"),
                ("Bookmark", "Bookmark"),
                ("Like", "Like"),
                ("Listen", "Listen"),
                ("Reply", "Reply"),
                ("Repost", "Repost"),
                ("Translation", "Translation"),
                ("Watch", "Watch"),
            ]
        ),
    )
    custom_content = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )


class ActionView(View):
    def get(self, request):
        articles = Article.objects.all()

        form = ActionForm(
            initial={
                "target": settings.DEFAULT_MENTION_TARGET,
                "author": "Author Authorson",
            }
        )

        return render(
            request,
            "actions.html",
            context={
                **default_context,
                "articles": articles,
                "action_form": form,
                "mentions": get_mentions_for_url(config.build_url(reverse("actions"))),
            },
        )

    def post(self, request):
        form = ActionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            author = data.get("author")
            target_url = data.get("target")
            mention_type = data.get("type")
            content = data.get("custom_content")

            create_article(
                author=author,
                target_url=target_url,
                mention_type=mention_type,
                content=content,
            )

            return HttpResponse(status=202)

        else:
            log.warning(f"Invalid form: {form}, {request.POST}")
            for field in form:
                log.warning(f"- {field.name}: {field.errors}")
            return HttpResponse(status=400)


class TimeoutView(View):
    """A view which takes too long to respond."""

    def get(self, request):
        time.sleep(options.timeout() + 1)
        return HttpResponse("That took a while!", status=200)


class MaybeTimeoutView(View):
    def get(self, request):
        timed_out = random.random() > 0.4

        if timed_out:
            log.info("MaybeTimeoutView timed out!")
            time.sleep(options.timeout() + 1)

        return HttpResponse(f"timed_out={timed_out}", status=200)
