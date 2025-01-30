from datetime import date
from unittest import skipIf

from django.test.utils import override_settings
from django.urls import include, path

from mentions import resolution
from mentions.exceptions import (
    NoModelForUrlPath,
    OptionalDependency,
    TargetDoesNotExist,
)
from tests.config.urls import urlpatterns as base_urlpatterns
from tests.tests.util import testfunc
from tests.tests.util.testcase import WebmentionTestCase

try:
    import wagtail

    wagtail_version = wagtail.__version__
    major, *rest = wagtail_version.split(".")
    wagtail_has_path_decorator = int(major) >= 4

    from wagtail import urls as wagtail_urls
    from wagtail.models import Page, Site

    from tests.test_wagtail_app.models import IndexPage, MentionablePage, SimplePage
except ImportError:
    Page = None
    SimplePage = None
    Site = None
    IndexPage = None
    MentionablePage = None
    wagtail_urls = {"urlpatterns": []}
    wagtail_has_path_decorator = False


urlpatterns = base_urlpatterns + [
    path("wagtail/", include(wagtail_urls)),
]


try:
    import wagtail
except ImportError:
    wagtail = None


@skipIf(wagtail is None, reason="Wagtail is not installed")
@override_settings(ROOT_URLCONF=__name__)
class WagtailTestCase(WebmentionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.simple_page = SimplePage(title="simple-page")
        self.target = MentionablePage(title="such content", date=date(2022, 11, 16))

        pages = [self.simple_page, self.target]

        site: Site = Site.objects.first()
        root = site.root_page.specific

        blog_index = IndexPage(title="pages")
        root.add_child(instance=blog_index)
        site.root_page = blog_index

        for page in pages:
            blog_index.add_child(instance=page)

    def build_url(self, url: str) -> str:
        return f"/wagtail/pages/{url}"

    def test_wagtail(self):
        self.assertIsNotNone(wagtail)

    def assert_resolves_target(self, url: str):
        url = self.build_url(url)
        print(f"URL: {url}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        result = resolution.get_model_for_url(url)
        self.assertEqual(self.target, result)


@skipIf(not wagtail_has_path_decorator, "@path decorator not available until v4")
class PathWagtailTests(WagtailTestCase):
    def test_page_lookup(self):
        url = "such-content/"
        self.assert_resolves_target(url)

    def test_page_lookup_by_altpath_default_lookup(self):
        url = f"{self.target.pk}/"
        self.assert_resolves_target(url)

    def test_page_lookup_by_altpath(self):
        url = "2022/11/16/"
        self.assert_resolves_target(url)

    def test_autopage(self):
        url = "autopage/2022/11/16/"
        self.assert_resolves_target(url)


class RePathWagtailTests(WagtailTestCase):
    def test_page_lookup_with_named_groups(self):
        url = "named/2022/11/such-content/"
        self.assert_resolves_target(url)

    def test_page_lookup_with_unnamed_groups(self):
        url = "unnamed/2022/11/such-content/"
        self.assert_resolves_target(url)

    def test_page_lookup_with_string_model_class(self):
        url = "string_model_class/2022/11/such-content/"
        self.assert_resolves_target(url)

    def test_page_lookup_with_string_qualified_model_class(self):
        url = "string_model_class_with_appname/2022/11/such-content/"
        self.assert_resolves_target(url)

    def test_autopage_unnamed_groups(self):
        url = "autopage/unnamed/2022/11/such-content/"
        self.assert_resolves_target(url)

    def test_autopage_named_groups(self):
        url = "autopage/named/2022/11/such-content/"
        self.assert_resolves_target(url)

    def test_autopage_page_lookup_with_string_model_class(self):
        url = "autopage/string_model_class/2022/11/such-content/"
        self.assert_resolves_target(url)

    def test_autopage_page_lookup_with_string_qualified_model_class(self):
        url = "autopage/string_model_class_with_appname/2022/11/such-content/"
        self.assert_resolves_target(url)


class MiscWagtailTests(WagtailTestCase):
    def test_page_lookup_does_not_exist(self):
        with self.assertRaises(TargetDoesNotExist):
            resolution.get_model_for_url(self.build_url("does-not-exist/"))

    def test_non_page_still_accessible(self):
        obj = testfunc.create_mentionable_object()
        result = resolution.get_model_for_url(obj.get_absolute_url())

        self.assertEqual(obj, result)

    def test_page_without_mentionablemixin(self):
        with self.assertRaises(NoModelForUrlPath):
            resolution.get_model_for_url(self.build_url("simple-page/"))

    @skipIf(wagtail_has_path_decorator, "Only applies to wagtail version 3")
    def test_page_lookup_by_altpath_wagtail_v3(self):
        url = "2022/11/16/"
        with self.assertRaises(OptionalDependency):
            self.assert_resolves_target(url)
