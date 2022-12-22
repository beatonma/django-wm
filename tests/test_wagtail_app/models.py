from django.db import models
from django.http import Http404
from django.utils import timezone

from mentions.models.mixins import MentionableMixin

try:
    from wagtail.contrib.routable_page.models import RoutablePageMixin
    from wagtail.fields import RichTextField
    from wagtail.models import Page
    from wagtail.templatetags.wagtailcore_tags import richtext

    from mentions.helpers.thirdparty.wagtail import (
        mentions_wagtail_path,
        mentions_wagtail_re_path,
    )

    class SimplePage(Page):
        # Page without MentionableMixin
        pass

    class MentionablePage(MentionableMixin, Page):
        body = RichTextField(blank=True)
        date = models.DateField(default=timezone.now)

        def get_absolute_url(self):
            return self.get_url()

        def get_content_html(self) -> str:
            return richtext(self.body)

    class IndexPage(RoutablePageMixin, Page):
        @mentions_wagtail_path(
            "<int:year>/<int:month>/<int:day>/",
            model_class=MentionablePage,
            model_filter_map={
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

        @mentions_wagtail_re_path(
            r"^named/(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>.+)/$",
            model_class=MentionablePage,
            model_filter_map={
                "year": "date__year",
                "month": "date__month",
                "slug": "slug",
            },
        )
        def post_by_date_slug_regex_with_named_groups(
            self, request, year, month, slug, *args
        ):
            return self._serve(
                request,
                MentionablePage.objects.get(
                    date__year=year,
                    date__month=month,
                    slug=slug,
                ),
            )

        @mentions_wagtail_re_path(
            r"^unnamed/(\d{4})/(\d{2})/(.+)/$",
            model_class=MentionablePage,
            model_filters=("date__year", "date__month", "slug"),
        )
        def post_by_date_slug_regex_with_unnamed_groups(
            self, request, year, month, slug
        ):
            return self._serve(
                request,
                MentionablePage.objects.get(
                    date__year=year,
                    date__month=month,
                    slug=slug,
                ),
            )

        @mentions_wagtail_path(
            "autopage/<int:year>/<int:month>/<int:day>/",
            model_class=MentionablePage,
            model_filter_map={
                "year": "date__year",
                "month": "date__month",
                "day": "date__day",
            },
            autopage=True,
        )
        def autopage_post_by_date(self, request, page):
            return self._serve(request, page)

        @mentions_wagtail_re_path(
            r"^autopage/named/(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>.+)/$",
            model_class=MentionablePage,
            model_filter_map={
                "year": "date__year",
                "month": "date__month",
                "slug": "slug",
            },
            autopage=True,
        )
        def autopage_post_by_date_slug_regex_with_named_groups(self, request, page):
            return self._serve(request, page)

        @mentions_wagtail_re_path(
            r"^autopage/unnamed/(\d{4})/(\d{2})/(.+)/$",
            model_class=MentionablePage,
            model_filters=("date__year", "date__month", "slug"),
            autopage=True,
        )
        def autopage_post_by_date_slug_regex_with_unnamed_groups(self, request, page):
            return self._serve(request, page)

        @mentions_wagtail_re_path(
            r"^string_model_class/(\d{4})/(\d{2})/(.+)/$",
            model_class="MentionablePage",
            model_filters=("date__year", "date__month", "slug"),
        )
        def post_by_date_slug_with_str_model_class(self, request, year, month, slug):
            return self._serve(
                request,
                MentionablePage.objects.get(
                    date__year=year,
                    date__month=month,
                    slug=slug,
                ),
            )

        @mentions_wagtail_re_path(
            r"^string_model_class_with_appname/(\d{4})/(\d{2})/(.+)/$",
            model_class="test_wagtail_app.MentionablePage",
            model_filters=("date__year", "date__month", "slug"),
        )
        def post_by_date_slug_with_str_model_class_with_appname(
            self, request, year, month, slug
        ):
            return self._serve(
                request,
                MentionablePage.objects.get(
                    date__year=year,
                    date__month=month,
                    slug=slug,
                ),
            )

        @mentions_wagtail_re_path(
            r"^autopage/string_model_class/(\d{4})/(\d{2})/(.+)/$",
            model_class="MentionablePage",
            model_filters=("date__year", "date__month", "slug"),
            autopage=True,
        )
        def autopage_post_by_date_slug_with_str_model_class(self, request, page):
            return self._serve(request, page)

        @mentions_wagtail_re_path(
            r"^autopage/string_model_class_with_appname/(\d{4})/(\d{2})/(.+)/$",
            model_class="test_wagtail_app.MentionablePage",
            model_filters=("date__year", "date__month", "slug"),
            autopage=True,
        )
        def autopage_post_by_date_slug_with_str_model_class_with_appname(
            self, request, page
        ):
            return self._serve(request, page)

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
