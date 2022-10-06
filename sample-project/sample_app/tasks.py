import logging
import random

from django.conf import settings
from sample_app.compat import IncomingMentionType
from sample_app.models import Article, create_article

from mentions import options

log = logging.getLogger(__name__)


def create_initial_articles():
    Article.objects.get_or_create(
        title=f"First article on {options.domain_name()}",
        defaults={
            "content": "Something to talk about",
            "author": "A. Mouse",
        },
    )

    Article.objects.get_or_create(
        title=f"Article with self-referencing #IDs",
        defaults={
            "allow_outgoing_webmentions": True,
            "author": "A. Mouse",
            "content": """
            <p id="s2"><a href="#s2" >§</a> Some text</p>
            <p id="s3"><a href="#s3" >§</a> Some more text</p>
            """,
        },
    )


def automention():
    url = random.choice(settings.AUTOMENTION_URLS)
    create_article(
        author="automention",
        target_url=url,
        mention_type=random.choice(list(IncomingMentionType.__members__.keys())),
    )
    log.info(f"automention: mentioned url {url}")
