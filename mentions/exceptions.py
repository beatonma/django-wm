class WebmentionsException(Exception):
    """Base class for mentions-specific exceptions."""

    pass


class IncomingWebmentionException(WebmentionsException):
    """Base class for an error that occurs while handling a received webmention."""

    pass


class OutgoingWebmentionException(WebmentionsException):
    """Base class for an error that occurs while trying to send a webmention."""

    pass


class TargetWrongDomain(IncomingWebmentionException):
    """Target URL does not point to any domain in settings.ALLOWED_HOSTS."""

    pass


class TargetDoesNotExist(IncomingWebmentionException):
    """Target URL does not point to an object on our server."""

    pass


class SourceNotAccessible(IncomingWebmentionException):
    """Source URL does not exist, or returns an error code."""

    pass


class SourceDoesNotLink(IncomingWebmentionException):
    """Source URL exists but does not contain link to our content."""

    pass


class TargetNotAccessible(OutgoingWebmentionException):
    """Target URL does not exist, or returns an error code."""

    pass


class BadConfig(WebmentionsException):
    """URL resolution completed but did not include required data.

    The returned ResolverMatch.kwargs object must have entries for:
        - 'model_name'
        - 'slug'
    """

    pass


class ImplementationRequired(WebmentionsException):
    """A MentionableMixin model has not implemented a required method."""

    pass


class NotEnoughData(WebmentionsException):
    """Attempted to build a model instance but did not have enough data to do so."""

    pass
