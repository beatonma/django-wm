"""Exceptions raised by the `mentions` app.

Any other exceptions raised should be caught and/or wrapped by one of
these exception classes."""


class WebmentionsException(Exception):
    """Base class for mentions-specific exceptions."""

    pass


class IncomingWebmentionException(WebmentionsException):
    """Base class for an error that occurs while handling a received webmention."""

    pass


class OutgoingWebmentionException(WebmentionsException):
    """Base class for an error that occurs while trying to send a webmention."""

    pass


class WebmentionsConfigurationException(WebmentionsException):
    """Base class for an error related to `django-wm` setup."""

    pass


class BadUrlConfig(WebmentionsConfigurationException):
    """URL resolution completed but did not include required data."""

    pass


class ImplementationRequired(WebmentionsConfigurationException):
    """A MentionableMixin model has not implemented a required method."""

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


class RejectedByConfig(IncomingWebmentionException):
    """The mention is being rejected due to the current settings configuration."""

    pass


class NoModelForUrlPath(IncomingWebmentionException):
    """URL resolved to a `urlpattern` which did not include `model_name` kwarg."""

    pass


class TargetNotAccessible(OutgoingWebmentionException):
    """Target URL does not exist, or returns an error code."""

    pass


class NotEnoughData(WebmentionsException):
    """Attempted to build a model instance but did not have enough data to do so."""

    pass


class OptionalDependency(WebmentionsException):
    """Attempted to use an optional dependency which is not installed."""

    pass
