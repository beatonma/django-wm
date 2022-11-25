import random

from django.conf import settings
from sample_app_wagtail.models import BlogIndexPage, BlogPage, SimplePage
from wagtail.models import Site

from mentions.models.mixins import IncomingMentionType


def create_initial_pages():
    if BlogIndexPage.objects.all().exists():
        return

    site: Site = Site.objects.get(is_default_site=True)
    root = site.root_page.localized.specific

    index = BlogIndexPage(title="Blog", intro="Blog introduction")

    root.add_child(instance=index)
    site.root_page = index
    site.save(update_fields=["root_page"])

    simple_page = SimplePage(title="non-mentionable")
    index.add_child(instance=simple_page)

    blog = BlogPage(
        author="wagtail",
        title=f"initial blogpost",
        body=f"This is blog content.",
        overview=f"Initial blog blurb",
    )
    index.add_child(instance=blog)


def automention():
    BlogPage.create(
        author="automention",
        target_url=random.choice(settings.AUTOMENTION_URLS),
        mention_type=random.choice(list(IncomingMentionType.__members__.keys())),
    )
