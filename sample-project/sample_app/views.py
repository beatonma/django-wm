import logging
import random
import time

from django import forms
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from sample_app.models import Article, create_article

from mentions import options

log = logging.getLogger(__name__)


class ArticleView(View):
    def get(self, request, article_id: int, *args, **kwargs):
        article = Article.objects.get(pk=article_id)
        return render(
            request,
            "article.html",
            context={
                "DOMAIN_NAME": settings.DOMAIN_NAME,
                "DEFAULT_TARGET": settings.DEFAULT_MENTION_TARGET,
                "article": article,
            },
        )


class ActionForm(forms.Form):
    target = forms.CharField(required=True)
    author = forms.CharField(required=True, max_length=64)
    type = forms.CharField(required=False, max_length=64)


class ActionView(View):
    def get(self, request):
        from mentions.models import OutgoingWebmentionStatus, Webmention

        outgoing_mentions = OutgoingWebmentionStatus.objects.all().order_by(
            "-created_at"
        )
        received_mentions = Webmention.objects.all().order_by("-created_at")
        articles = Article.objects.all()

        return render(
            request,
            "actions.html",
            context={
                "DOMAIN_NAME": settings.DOMAIN_NAME,
                "DEFAULT_MENTION_TARGET": settings.DEFAULT_MENTION_TARGET,
                "DEFAULT_MENTION_AUTHOR": "Author Authorson",
                "OUTGOING_MENTIONS": outgoing_mentions,
                "RECEIVED_MENTIONS": received_mentions,
                "articles": articles,
            },
        )

    def post(self, request):
        form = ActionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            author = data.get("author")
            target_url = data.get("target")
            mention_type = data.get("type")

            create_article(
                author=author,
                target_url=target_url,
                mention_type=mention_type,
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
