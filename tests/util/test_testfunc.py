from unittest import TestCase

from mentions.util import get_url_validator
from tests.util import testfunc


class TestFuncTests(TestCase):
    """TESTS: Make sure test functions work as expected."""

    def test_random_url(self):
        """Randomly generated URLs are valid."""
        urls = [testfunc.random_url()] * 100
        validator = get_url_validator()

        for url in urls:
            validator(url)  # Throws ValidationError if invalid
