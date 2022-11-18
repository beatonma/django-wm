from datetime import date

from django.test.utils import override_settings
from django.urls import include, path

from mentions import resolution
from mentions.exceptions import TargetDoesNotExist
from tests.test_wagtail import WagtailTestCase
from tests.util import testfunc

try:
    from wagtail import urls as wagtail_urls
    from wagtail.models import Page, Site

    from wagtail_test_app.models import IndexPage, MentionablePage
except ImportError:
    Page = None
    Site = None
    IndexPage = None
    MentionablePage = None
    wagtail_urls = {"urlpatterns": []}

from tests.config.test_urls import urlpatterns as base_urlpatterns

urlpatterns = base_urlpatterns + [
    path("wagtail/", include(wagtail_urls)),
]


@override_settings(ROOT_URLCONF=__name__)
class WagtailTests(WagtailTestCase):
    def setUp(self) -> None:
        super().setUp()
        testfunc.create_mentionable_object()
        root = Site.objects.first().root_page.specific
        blog_index = IndexPage(title="pages")
        root.add_child(instance=blog_index)
        blog_index.refresh_from_db()

        decoy_one = MentionablePage(title="oh wow", date=date(2022, 11, 15))
        self.target = MentionablePage(title="such content", date=date(2022, 11, 16))
        decoy_two = MentionablePage(title="very impressive", date=date(2022, 11, 17))
        testfunc.create_mentionable_object()

        pages = [decoy_one, self.target, decoy_two]

        for page in pages:
            blog_index.add_child(instance=page)

    def test_page_lookup(self):
        result = resolution.get_model_for_url("/wagtail/pages/such-content/")
        self.assertEqual(self.target, result)

    def test_page_lookup_by_altpath(self):
        url = "/wagtail/pages/2022/11/16/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        result = resolution.get_model_for_url(url)
        self.assertEqual(self.target, result)

    def test_page_lookup_by_regex_altpath(self):
        url = "/wagtail/pages/2022/11/such-content/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        result = resolution.get_model_for_url(url)
        self.assertEqual(self.target, result)

    def test_page_lookup_by_altpath_default_lookup(self):
        url = f"/wagtail/pages/{self.target.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        result = resolution.get_model_for_url(url)
        self.assertEqual(self.target, result)

    def test_page_lookup_does_not_exist(self):
        with self.assertRaises(TargetDoesNotExist):
            resolution.get_model_for_url("/wagtail/pages/does-not-exist/")

    def test_non_page_still_accessible(self):
        obj = testfunc.create_mentionable_object()
        result = resolution.get_model_for_url(obj.get_absolute_url())

        self.assertEqual(obj, result)
