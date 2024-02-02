from django.test.utils import override_settings
from django.utils import timezone

from mentions import config, resolution
from mentions.exceptions import TargetDoesNotExist
from mentions.helpers.urls import mentions_path, mentions_re_path
from mentions.resolution import get_model_for_url
from tests.config.urls import core_urlpatterns
from tests.test_app.models import (
    MentionableTestBlogPost,
    MentionableTestModel,
    SampleBlog,
)
from tests.tests.util import testfunc
from tests.tests.util.testcase import WebmentionTestCase


def viewfunc():
    pass


urlpatterns = [
    mentions_path(
        "with_helper_config/<int:arbitrary_name>/",
        viewfunc,
        model_class=MentionableTestModel,
        model_filter_map={"arbitrary_name": "id"},
    ),
    mentions_path(
        "blogs/<slug:blog_slug>/<int:year>/<int:month>/<int:day>/<slug:post_slug>/",
        viewfunc,
        model_class=MentionableTestBlogPost,
        model_filter_map={
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
        model_filter_map=[
            ("mapping_as_sequence", "id"),
        ],
    ),
    mentions_path(
        "model_filter_map_omitted/<int:id>",
        viewfunc,
        model_class=MentionableTestModel,
    ),
    mentions_re_path(
        r"regexpath/[0-9]+/(?P<regex_name>[\w-]+)/",
        viewfunc,
        model_class=MentionableTestModel,
        model_filter_map={
            "regex_name": "name",
        },
    ),
    mentions_re_path(
        r"unnamed_re_path/([\w-]+)/[0-9]+/",
        viewfunc,
        model_class=MentionableTestModel,
        model_filters=["name"],
    ),
    mentions_path(
        "fqn_string_class/<int:id>/",
        viewfunc,
        model_class="test_app.MentionableTestModel",
    ),
] + core_urlpatterns


@override_settings(ROOT_URLCONF=__name__)
class UrlpatternsHelperTests(WebmentionTestCase):
    def test_mentions_path_resolves_model(self):
        obj = testfunc.create_mentionable_object()

        retrieved_obj = get_model_for_url(
            config.build_url(f"/with_helper_config/{obj.id}/")
        )
        self.assertEqual(obj, retrieved_obj)

    def test_mentions_path_with_complex_mapping_resolves_model(self):
        published = timezone.datetime(2022, 3, 28, 9, 3, 2, tzinfo=timezone.get_current_timezone())

        blog = SampleBlog.objects.create(slug="blog-slug")
        MentionableTestBlogPost.objects.create(
            blog=blog,
            content="hello am decoy",
            slug="testpostslug",
            timestamp=timezone.datetime(2022, 3, 27, 9, 3, 2, tzinfo=timezone.get_current_timezone()),
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
        obj = testfunc.create_mentionable_object(id=1432)

        retrieved_object = resolution.get_model_for_url(
            "/with_sequence_field_mapping/1432"
        )
        self.assertEqual(obj, retrieved_object)

    def test_mentions_path_with_mapping_omitted(self):
        obj = testfunc.create_mentionable_object(id=9861)

        retrieved_object = resolution.get_model_for_url(
            "/model_filter_map_omitted/9861"
        )
        self.assertEqual(obj, retrieved_object)

    def test_mentions_re_path(self):
        obj = testfunc.create_mentionable_object(name="regex-model")

        retrieved_object = resolution.get_model_for_url("/regexpath/1243/regex-model/")

        self.assertEqual(obj, retrieved_object)

        with self.assertRaises(TargetDoesNotExist):
            resolution.get_model_for_url("/regexpath/abc/regex-model/")

    def test_mentions_re_path_with_unnamed_groups(self):
        obj = testfunc.create_mentionable_object(name="regex-model")

        retrieved_object = resolution.get_model_for_url(
            "/unnamed_re_path/regex-model/1243/"
        )

        self.assertEqual(obj, retrieved_object)

        with self.assertRaises(TargetDoesNotExist):
            resolution.get_model_for_url("/unnamed_re_path/regex-model/abc/")

    def test_mentions_path_with_fqn_string_model_class(self):
        obj = testfunc.create_mentionable_object(id=37)

        retrieved_object = resolution.get_model_for_url("/fqn_string_class/37/")
        self.assertEqual(obj, retrieved_object)
