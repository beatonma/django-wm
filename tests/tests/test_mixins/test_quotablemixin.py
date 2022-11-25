from mentions.models.mixins import IncomingMentionType
from tests.tests.util.testcase import WebmentionTestCase


class QuotableMixinTests(WebmentionTestCase):
    """MODELS: QuotableMixin tests"""

    def test_choices(self):
        """Choices for QuotableMixin.post_type are correct."""
        choices = IncomingMentionType.choices()

        self.assertTrue(("reply", "Reply") in choices)
        self.assertTrue(("like", "Like") in choices)
