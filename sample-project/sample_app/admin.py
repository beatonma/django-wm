from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from sample_app.models import Article

from mentions.models import Webmention


class MentionInline(GenericStackedInline):
    model = Webmention

    fields = [
        "source_url",
        "target_url",
    ]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "pk",
        "author",
    ]

    inlines = [
        MentionInline,
    ]
