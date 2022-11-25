import random
import uuid
from typing import Optional

from django.core.management import BaseCommand
from sample_app.models import Article
from sample_app.tasks import create_initial_articles

from mentions import config
from mentions.models import HCard, OutgoingWebmentionStatus, Webmention

"""
Create multiple HCards for target.
Create multiple OutgoingWebmentionStatus for target.
"""


class Command(BaseCommand):
    """Create sample data that may be found in an existing installation.

    This will be used to check that potentially problematic data is handled
    gracefully after upgrading the django-wm library."""

    def handle(self, *args, **options):
        create_initial_articles()
        _create_hcards()
        _create_webmentions()


def _create_hcards():
    homepage = _random_domain()
    name = "automention"

    HCard.objects.create(name=name, homepage=homepage)
    HCard.objects.create(name=name)
    HCard.objects.create(name=name, homepage=_random_domain())


def _create_webmentions():
    for n in range(3):
        hcard = (
            random.choice(list(HCard.objects.all())) if random.random() > 0.67 else None
        )

        _create_webmention(
            source_url=_random_url(),
            target_url=config.build_url(Article.objects.first().get_absolute_url()),
            hcard=hcard,
        )

    target_url = _random_url()
    for n in range(2):
        OutgoingWebmentionStatus.objects.create(
            source_url=Article.objects.first().get_absolute_url(),
            target_url=target_url,
            successful=True,
        )


def _create_webmention(
    source_url: Optional[str] = None,
    target_url: Optional[str] = None,
    sent_by: Optional[str] = None,
    approved: bool = True,
    validated: bool = True,
    quote: Optional[str] = None,
    hcard: Optional[HCard] = None,
) -> Webmention:
    return Webmention.objects.create(
        source_url=source_url or _random_url(),
        target_url=target_url or _random_url(),
        sent_by=sent_by or _random_url(),
        approved=approved,
        validated=validated,
        quote=quote,
        hcard=hcard,
    )


def _random_str(length: int = 5) -> str:
    """Generate a short string of random characters."""
    return uuid.uuid4().hex[:length]


def _random_domain() -> str:
    """Return a randomised domain name."""
    return f"example-url-{_random_str()}.org"


def _random_url() -> str:
    """Generate a random URL."""
    scheme = random.choice(["http", "https"])
    subdomain = random.choice(["", "", f"{_random_str()}."])
    domain = _random_domain()
    port = random.choice(([""] * 5) + [":8000"])
    path = "/".join([_random_str() for _ in range(random.randint(0, 2))])
    path = (f"/{path}" if path else "") + random.choice(["", "/"])

    return f"{scheme}://{subdomain}{domain}{port}{path}"
