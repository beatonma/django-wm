import logging
import random

from django.conf import settings
from sample_app.compat import IncomingMentionType
from sample_app.models import Article, create_article

log = logging.getLogger(__name__)


def create_initial_article():
    Article.objects.get_or_create(
        title=f"First article on {settings.DOMAIN_NAME}",
        defaults={
            "content": "Something to talk about",
            "author": "A. Mouse",
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
