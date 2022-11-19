from django.db import models
from django.http import Http404
from django.utils import timezone

from mentions.helpers.thirdparty.wagtail import (
    mentions_wagtail_path,
    mentions_wagtail_re_path,
)
from mentions.models.mixins import MentionableMixin

try:
    from wagtail.contrib.routable_page.models import RoutablePageMixin, path
    from wagtail.fields import RichTextField
    from wagtail.models import Page

    class SimplePage(Page):
        # Page without MentionableMixin
        pass

    class MentionablePage(MentionableMixin, Page):
        body = RichTextField(blank=True)
        date = models.DateField(default=timezone.now)

        def get_absolute_url(self):
            return self.get_url()

        def get_content_html(self) -> str:
            return self.body

    class IndexPage(RoutablePageMixin, Page):
        @mentions_wagtail_path(
            "<int:year>/<int:month>/<int:day>/",
            MentionablePage,
            model_field_mapping={
                "year": "date__year",
                "month": "date__month",
                "day": "date__day",
            },
        )
        def post_by_date(self, request, year, month, day):
            return self._serve(
                request,
                page=MentionablePage.objects.get(
                    date__year=year,
                    date__month=month,
                    date__day=day,
                ),
            )

        @mentions_wagtail_re_path(
            r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>.+)/$",
            MentionablePage,
            {"year": "date__year", "month": "date__month", "slug": "slug"},
        )
        def post_by_date_slug_regex(self, request, year, month, slug):
            return self._serve(
                request,
                MentionablePage.objects.get(
                    date__year=year,
                    date__month=month,
                    slug=slug,
                ),
            )

        @mentions_wagtail_path(
            "<int:pk>/",
            MentionablePage,
        )
        def post_by_pk(self, request, pk):
            return self._serve(
                request,
                page=MentionablePage.objects.get(
                    pk=pk,
                ),
            )

        def _serve(self, request, page):
            if not page:
                raise Http404

            return page.serve(request)

        def __str__(self):
            return f"IndexPage {self.slug}"

except ImportError:
    RichTextField = models.TextField
    Page = models.Model
    MentionablePage = None
