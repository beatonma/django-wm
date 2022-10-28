from django.test.utils import override_settings
from django.utils import timezone

from mentions import config, resolution
from mentions.exceptions import TargetDoesNotExist
from mentions.helpers.urls import mentions_path, mentions_re_path
from mentions.resolution import get_model_for_url
from tests import WebmentionTestCase
from tests.config.test_urls import core_urlpatterns
from tests.models import MentionableTestBlogPost, MentionableTestModel, SampleBlog


def viewfunc():
    pass


urlpatterns = [
    mentions_path(
        "with_helper_config/<int:arbitrary_name>/",
        viewfunc,
        model_class=MentionableTestModel,
        model_field_mapping={"arbitrary_name": "id"},
    ),
    mentions_path(
        "blogs/<slug:blog_slug>/<int:year>/<int:month>/<int:day>/<slug:post_slug>/",
        viewfunc,
        model_class=MentionableTestBlogPost,
        model_field_mapping={
            "blog_slug": "blog__slug__exact",
            "year": "timestamp__year",
            "month": "timestamp__month",
            "day": "timestamp__day",
            "post_slug": "slug",
        },
    ),
    mentions_path(
        "with_sequence_field_mapping/<int:mapping_as_sequence>",
        viewfunc,
        model_class=MentionableTestModel,
        model_field_mapping=[
            ("mapping_as_sequence", "id"),
        ],
    ),
    mentions_path(
        "model_field_mapping_omitted/<int:id>",
        viewfunc,
        model_class=MentionableTestModel,
    ),
    mentions_re_path(
        r"regexpath/[0-9]+/(?P<regex_name>[\w-]+)/",
        viewfunc,
        model_class=MentionableTestModel,
        model_field_mapping={
            "regex_name": "name",
        },
    ),
    *core_urlpatterns,
]


@override_settings(ROOT_URLCONF=__name__)
class UrlpatternsHelperTests(WebmentionTestCase):
    def test_mentions_path_resolves_model(self):
        obj = MentionableTestModel.objects.create()

        retrieved_obj = get_model_for_url(
            config.build_url(f"/with_helper_config/{obj.id}/")
        )
        self.assertEqual(obj, retrieved_obj)

    def test_mentions_path_with_complex_mapping_resolves_model(self):
        published = timezone.datetime(2022, 3, 28, 9, 3, 2)

        blog = SampleBlog.objects.create(slug="blog-slug")
        MentionableTestBlogPost.objects.create(
            blog=blog,
            content="hello am decoy",
            slug="testpostslug",
            timestamp=timezone.datetime(2022, 3, 27, 9, 3, 2),
        )
        MentionableTestBlogPost.objects.create(
            blog=blog,
            content="wholesome content",
            slug="wholesome-post",
            timestamp=published,
        )
        MentionableTestBlogPost.objects.create(
            blog=blog,
            content="hello am decoy",
            slug="testpostslug",
            timestamp=published,
        )

        retrieved_object = resolution.get_model_for_url(
            "/blogs/blog-slug/2022/3/28/wholesome-post/"
        )

        self.assertEqual(retrieved_object.content, "wholesome content")

        with self.assertRaises(TargetDoesNotExist):
            resolution.get_model_for_url(
                "/blogs/blog-slug/2022/3/29/something-different/"
            )

    def test_mentions_path_with_mapping_as_sequence(self):
        obj = MentionableTestModel.objects.create(id=1432)

        retrieved_object = resolution.get_model_for_url(
            "/with_sequence_field_mapping/1432"
        )
        self.assertEqual(obj, retrieved_object)

    def test_mentions_path_with_mapping_omitted(self):
        obj = MentionableTestModel.objects.create(id=9861)

        retrieved_object = resolution.get_model_for_url(
            "/model_field_mapping_omitted/9861"
        )
        self.assertEqual(obj, retrieved_object)

    def test_mentions_re_path(self):
        MentionableTestModel.objects.create()
        obj = MentionableTestModel.objects.create(name="regex-model")
        MentionableTestModel.objects.create()

        retrieved_object = resolution.get_model_for_url("/regexpath/1243/regex-model/")

        self.assertEqual(obj, retrieved_object)

        with self.assertRaises(TargetDoesNotExist):
            resolution.get_model_for_url("/regexpath/abc/regex-model/")
