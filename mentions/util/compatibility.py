"""Backport features of newer Python releases than our minimum target version.

All functions should contain information about their standard library equivalent
and the Python version in which it becomes available.

These should be removed and replaced with standard library equivalents when
we update our minimum target version."""


def removeprefix(text: str, prefix: str) -> str:
    """Backport of `str.removeprefix` introduced in Python 3.9"""
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def removesuffix(text: str, suffix: str) -> str:
    """Backport of `str.removesuffix` introduced in Python 3.9"""
    if text.endswith(suffix):
        return text[: -len(suffix)]
    return text
