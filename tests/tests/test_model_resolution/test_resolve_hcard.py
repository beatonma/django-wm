from mentions.models import HCard
from mentions.models.hcard import update_or_create_hcard
from tests.tests.util.testcase import WebmentionTestCase


class HCardResolutionTests(WebmentionTestCase):
    def test_hcard_field_precedence(self):
        """Retrieve HCard using fields with correct order of precedence: [homepage, name, avatar]"""

        full_hcard = HCard.objects.create(
            homepage="https://beatonma.org",
            name="Michael Beaton",
            avatar="https://beatonma.org/static/images/avatar.jpg",
            json="{}",
        )
        homepage = HCard.objects.create(
            homepage="https://beatonma.org",
            avatar="https://beatonma.org/static/images/avatar.jpg",
            json="{}",
        )
        name = HCard.objects.create(
            name="Michael Beaton",
            avatar="https://beatonma.org/static/images/avatar.jpg",
            json="{}",
        )
        avatar_only = HCard.objects.create(
            avatar="https://beatonma.org/static/images/avatar.jpg",
            json="{}",
        )

        self.assertEqual(
            update_or_create_hcard(
                homepage="https://beatonma.org",
                name="Michael Beaton",
                avatar="https://beatonma.org/static/images/avatar.jpg",
                data="{}",
            ),
            full_hcard,
        )

        self.assertEqual(
            update_or_create_hcard(
                homepage="https://beatonma.org",
                name=None,
                avatar="https://beatonma.org/static/images/avatar.jpg",
                data="{}",
            ),
            homepage,
        )

        self.assertEqual(
            update_or_create_hcard(
                homepage=None,
                name="Michael Beaton",
                avatar="https://beatonma.org/static/images/avatar.jpg",
                data="{}",
            ),
            name,
        )

        self.assertEqual(
            update_or_create_hcard(
                homepage=None,
                name=None,
                avatar="https://beatonma.org/static/images/avatar.jpg",
                data="{}",
            ),
            avatar_only,
        )
        self.assert_exists(HCard, count=4)

        # Multiple hcards may share the same homepage url if they have different names.
        update_or_create_hcard(
            homepage="https://beatonma.org",
            name="Michael Smith",
            avatar="https://beatonma.org/static/images/avatar.jpg",
            data="{}",
        ),
        self.assert_exists(HCard, count=5)

        # Multiple hcards may share the same name if they have different homepage urls.
        update_or_create_hcard(
            homepage="https://beatonma-alt.org",
            name="Michael Beaton",
            avatar="https://beatonma.org/static/images/avatar.jpg",
            data="{}",
        ),
        self.assert_exists(HCard, count=6)
