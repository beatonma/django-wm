import pytest


class PytestRunner:
    def run_tests(self, *args):
        return pytest.main(*args)
