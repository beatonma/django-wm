from mentions.util import get_url_validator
from tests.tests.util import testfunc
from tests.tests.util.testcase import SimpleTestCase


class TestFuncTests(SimpleTestCase):
    """TESTS: Make sure test functions work as expected."""

    def test_random_url(self):
        """Randomly generated URLs are valid."""
        urls = [testfunc.random_url()] * 100
        validator = get_url_validator()

        for url in urls:
            validator(url)  # Throws ValidationError if invalid
