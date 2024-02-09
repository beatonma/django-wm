from mentions.util.compatibility import removeprefix, removesuffix
from tests.tests.util.testcase import SimpleTestCase


class CompatibilityTests(SimpleTestCase):
    def test_str_removeprefix(self):
        func = removeprefix
        self.assertEqual(func("abcde", "ab"), "cde")
        self.assertEqual(func("1248", "1"), "248")

        self.assertEqual(func("abcde", "bc"), "abcde")
        self.assertEqual(func("abcde", "de"), "abcde")
        self.assertEqual(func("abcde", "abcdef"), "abcde")

    def test_str_removesuffix(self):
        func = removesuffix
        self.assertEqual(func("abcde", "de"), "abc")
        self.assertEqual(func("1248", "248"), "1")

        self.assertEqual(func("abcde", "ab"), "abcde")
        self.assertEqual(func("abcde", "abcd"), "abcde")
        self.assertEqual(func("abcde", "abcdef"), "abcde")
