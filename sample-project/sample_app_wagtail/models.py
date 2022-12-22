import logging
import uuid
from typing import Optional, Union

from django.db import models
from django.http import Http404
from django.utils import timezone
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index
from wagtail.templatetags.wagtailcore_tags import richtext

from mentions.helpers.thirdparty.wagtail import mentions_wagtail_path
from mentions.models.mixins import IncomingMentionType, MentionableMixin
from mentions.resolution import get_mentions_for_url

log = logging.getLogger(__name__)


class SimplePage(Page):
    """A Page that does not implement MentionableMixin.

    Cannot send mentions.

    Its URL is still mentionable but received mentions will not be attached to
    the page instance."""

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["mentions"] = get_mentions_for_url(self.url)
        return context


class BlogPage(MentionableMixin, Page):
    author = models.CharField(max_length=64, blank=True)
    overview = RichTextField(blank=True)
    body = RichTextField()
    date = models.DateField("Post date", default=timezone.now)

    content_panels = Page.content_panels + [
        FieldPanel("author"),
        FieldPanel("overview"),
        FieldPanel("body"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("overview"),
        index.SearchField("body"),
    ]

    def get_content_html(self) -> str:
        return f"{richtext(self.overview)} {richtext(self.body)}"

    def get_absolute_url(self):
        log.info(f"get_absolute_url: {self.url}")
        return self.url

    def should_process_webmentions(self) -> bool:
        """Return True if this instance should process webmentions when saved."""
        log.warning(f"should_process_webmentions: {self.live} [{self}]")
        return self.live

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["mentions"] = self.get_mentions()

        return context

    @classmethod
    def create(
        cls,
        author: str,
        target_url: str,
        mention_type: Union[str, IncomingMentionType],
        content: Optional[str] = None,
    ):
        title = f"blogpost-{uuid.uuid4().hex[:5]}"
        _type = IncomingMentionType.get_microformat_from_name(mention_type)

        content = (
            content
            or f"""<p><span>This text mentions <a href="{target_url}" class="{_type}">this page</a></span></p>"""
        )

        blog = BlogPage(
            author=author,
            title=title,
            body=content,
            overview=f"Blog blurb about {title}",
            allow_outgoing_webmentions=True,
        )
        index_page = BlogIndexPage.objects.get(title="Blog")
        index_page.add_child(instance=blog)


class BlogIndexPage(RoutablePageMixin, Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    @mentions_wagtail_path(
        "<int:year>/<int:month>/<slug:slug>/",
        BlogPage,
        model_filter_map={
            "year": "date__year",
            "month": "date__month",
            "slug": "slug",
        },
    )
    def post_by_date_slug(self, request, year, month, slug, *args, **kwargs):
        page = BlogPage.objects.get(
            date__year=year,
            date__month=month,
            slug=slug,
        )
        if not page:
            log.warning(f"Page not found: {request}")
            raise Http404

        return page.serve(request)
