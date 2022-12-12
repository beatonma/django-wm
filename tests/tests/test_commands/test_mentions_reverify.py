from io import StringIO

from django.core.management import call_command

from mentions.models import Webmention
from tests.tests.util import testfunc
from tests.tests.util.mocking import patch_http_get
from tests.tests.util.testcase import WebmentionTestCase


class MentionsReverifyTests(WebmentionTestCase):
    def test_command(self):
        Webmention.objects.create(
            target_url=testfunc.get_simple_url(),
            source_url=testfunc.random_url(),
            validated=False,
        )

        target_url = testfunc.get_simple_url()
        Webmention.objects.create(
            pk=101,
            target_url=target_url,
            source_url=testfunc.random_url(),
            validated=False,
        )
        Webmention.objects.create(
            target_url=testfunc.get_simple_url(),
            source_url=testfunc.random_url(),
            validated=False,
        )

        with patch_http_get(text=f"""<a href="{target_url}">link</a>"""):
            call_command(
                "mentions_reverify",
                "pk=101",
                stdout=StringIO(),
                stderr=StringIO(),
            )

        self.assertTrue(Webmention.objects.get(pk=101).validated)
        self.assertEqual(Webmention.objects.filter(validated=False).count(), 2)
