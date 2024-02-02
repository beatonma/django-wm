from django.http import HttpResponse
from django.test.utils import override_settings
from django.urls import path, register_converter
from django.utils import timezone
from django.views import View

from mentions import resolution
from tests.test_app.models import MentionableTestBlogPost, SampleBlog
from tests.tests.util import constants, snippets, testfunc
from tests.tests.util.testcase import WebmentionTestCase


class TwoDigitConverter:
    """Matches 2 digits."""

    regex = r"[0-9]{2}"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return f"{int(value):02d}"


register_converter(TwoDigitConverter, "mm")


class BlogPostView(View):
    """A view that is associated with a MentionableTestModel.

    Webmentions are retrieved via the associated model instance."""

    def get(
        self,
        request,
        *args,
        blog_slug: str,
        year: int,
        month: int,
        day: int,
        post_slug: str,
        **kwargs,
    ):
        obj = MentionableTestBlogPost.objects.get(
            blog__slug=blog_slug,
            timestamp__year=year,
            timestamp__month=month,
            timestamp__day=day,
            slug=post_slug,
        )
        html = snippets.html_all_endpoints(obj.content)
        response = HttpResponse(html, status=200)
        response["Link"] = snippets.http_header_link(
            testfunc.endpoint_submit_webmention_absolute()
        )
        return response


urlpatterns = [
    path(
        r"<slug:blog_slug>/<int:year>/<mm:month>/<int:day>/<slug:post_slug>/",
        BlogPostView.as_view(),
        kwargs={
            "model_name": constants.model_name_test_blogpost,
        },
    ),
]


@override_settings(ROOT_URLCONF=__name__)
class GetModelForUrlWithCustomObjectResolution(WebmentionTestCase):
    """INCOMING: Tests for get_model_for_url_path when MentionableMixin.resolve_from_url_kwargs has been overridden."""

    def setUp(self) -> None:
        super().setUp()
        self.published = timezone.datetime(2022, 3, 28, 9, 3, 2, tzinfo=timezone.get_current_timezone())

        blog = SampleBlog.objects.create(slug="blogslug")
        MentionableTestBlogPost.objects.create(
            blog=blog,
            content="hello am decoy",
            slug="testpostdecoyslug",
            timestamp=self.published,
        )
        self.blogpost = MentionableTestBlogPost.objects.create(
            blog=blog,
            content="hello am blog",
            slug="testpostslug",
            timestamp=self.published,
        )
        MentionableTestBlogPost.objects.create(
            blog=blog,
            content="hello am decoy",
            slug="testpostslug",
            timestamp=timezone.datetime(2022, 3, 27, 9, 3, 2, tzinfo=timezone.get_current_timezone()),
        )

    def test_get_model_for_url__with_custom_lookup(self):
        """Reverse URL lookup with custom resolve_from_url_kwargs implementation finds the correct object."""
        retrieved_object = resolution.get_model_for_url(
            "/blogslug/2022/03/28/testpostslug/"
        )

        self.assertEqual(retrieved_object, self.blogpost)
