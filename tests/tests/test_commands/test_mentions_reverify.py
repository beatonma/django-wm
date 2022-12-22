from django.core.management import call_command

from mentions.management.commands.mentions_reverify import parse_filter_value
from mentions.models import Webmention
from tests.tests.util import testfunc
from tests.tests.util.mocking import patch_http_get
from tests.tests.util.testcase import WebmentionTestCase


def _call_command(*args):
    return call_command(
        "mentions_reverify",
        *args,
    )


class MentionsReverifyTests(WebmentionTestCase):
    def test_command_with_filter(self):
        Webmention.objects.create(
            target_url=testfunc.get_absolute_url_for_object(),
            source_url=testfunc.random_url(),
            validated=False,
        )

        target_url = testfunc.get_absolute_url_for_object()
        Webmention.objects.create(
            pk=101,
            target_url=target_url,
            source_url=testfunc.random_url(),
            validated=False,
        )
        Webmention.objects.create(
            target_url=testfunc.get_absolute_url_for_object(),
            source_url=testfunc.random_url(),
            validated=False,
        )

        with patch_http_get(text=f"""<a href="{target_url}">link</a>"""):
            _call_command("pk=101")

        self.assertTrue(Webmention.objects.get(pk=101).validated)
        self.assert_exists(Webmention, validated=False, count=2)

    def test_command_all(self):
        Webmention.objects.create(
            target_url=testfunc.get_absolute_url_for_object(),
            source_url=testfunc.random_url(),
            validated=True,
        )  # Should in un-validated

        obj = testfunc.create_mentionable_object()
        target_url = testfunc.get_absolute_url_for_object(obj)
        Webmention.objects.create(
            pk=201,
            target_url=target_url,
            source_url=testfunc.random_url(),
            validated=False,
        )  # Should be validated
        Webmention.objects.create(
            target_url=testfunc.get_absolute_url_for_object(),
            source_url=testfunc.random_url(),
            validated=True,
        )  # Should in un-validated

        with patch_http_get(text=f"""<a href="{target_url}">link</a>"""):
            _call_command("--all")

        target = Webmention.objects.get(pk=201)
        self.assertTrue(target.validated)
        self.assertEqual(target.target_object, obj)
        self.assert_exists(Webmention, validated=False, count=2)

    def test_command_with_no_args(self):
        with self.assertRaises(ValueError):
            _call_command()

    def test_filter_parsing(self):
        self.assertTrue(parse_filter_value("True"))
        self.assertFalse(parse_filter_value("False"))

        self.assertEqual(3, parse_filter_value("3"))
        self.assertEqual(3.1, parse_filter_value("3.1"))

        self.assertEqual("string", parse_filter_value("string"))
