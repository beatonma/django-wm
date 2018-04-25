class TargetWrongDomain(Exception):
    """Target URL does not point to any domain in settings.ALLOWED_HOSTS."""

    pass


class TargetDoesNotExist(Exception):
    """Target URL does not point to an object on our server."""

    pass


class SourceNotAccessible(Exception):
    """Source URL does not exist, or returns an error code."""

    pass


class SourceDoesNotLink(Exception):
    """Source URL exists but does not contain link to our content."""

    pass


class BadConfig(Exception):
    """
    URL resolution completed but did not include required data.

    The returned ResolverMatch.kwargs object must have entries for:
        - 'model_name'
        - 'slug'
    """

    pass
