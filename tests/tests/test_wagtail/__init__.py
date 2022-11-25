import logging
from unittest import skipIf

from tests.tests.util.testcase import WebmentionTestCase

log = logging.getLogger(__name__)

try:
    import wagtail
except ImportError:
    wagtail = None


@skipIf(wagtail is None, reason="Wagtail is not installed")
class WagtailTestCase(WebmentionTestCase):
    def test_wagtail(self):
        self.assertIsNotNone(wagtail)
