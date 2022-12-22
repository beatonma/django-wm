import logging
import random

from django import forms
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from sample_app.models import Article, Blog, create_article
from sample_app.views import BaseView, default_context

from mentions import config
from mentions.resolution import get_mentions_for_url

log = logging.getLogger(__name__)


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


class ActionView(BaseView):
    def get(self, request):
        articles = list(Article.objects.all()) + list(Blog.objects.all())

        form = ActionForm(
            initial={
                "target": random.choice(settings.AUTOMENTION_URLS),
                "author": "Author Authorson",
            }
        )

        return render(
            request,
            "sample_app/actions.html",
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
