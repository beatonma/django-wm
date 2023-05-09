from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from mentions.models import (
    HCard,
    OutgoingWebmentionStatus,
    PendingIncomingWebmention,
    PendingOutgoingContent,
    SimpleMention,
    Webmention,
)
from mentions.models.managers.webmention import WebmentionQuerySet

RETRYABLEMIXIN_FIELDS = [
    "is_awaiting_retry",
    "last_retry_attempt",
    "retry_attempt_count",
]


@admin.action(permissions=["change"])
def mark_webmention_approved(modeladmin, request, queryset: WebmentionQuerySet):
    queryset.mark_as_approved()


@admin.action(permissions=["change"])
def mark_webmention_unapproved(modeladmin, request, queryset: WebmentionQuerySet):
    queryset.mark_as_unapproved()


@admin.action(permissions=["change"])
def mark_webmention_read(modeladmin, request, queryset: WebmentionQuerySet):
    queryset.mark_as_read()


@admin.action(permissions=["change"])
def mark_webmention_unread(modeladmin, request, queryset: WebmentionQuerySet):
    queryset.mark_as_unread()


class BaseAdmin(admin.ModelAdmin):
    save_on_top = True


class ClickableUrlMixin:
    def clickable_source_url(self, obj):
        return clickable_link(obj.source_url)

    clickable_source_url.short_description = _("source URL")

    def clickable_target_url(self, obj):
        return clickable_link(obj.target_url)

    clickable_target_url.short_description = _("target URL")


class TextAreaForm(forms.ModelForm):
    class Meta:
        widgets = {
            "quote": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


@admin.register(SimpleMention)
class QuotableAdmin(BaseAdmin):
    form = TextAreaForm
    date_hierarchy = "published"
    list_display = [
        "source_url",
        "target_url",
        "get_hcard_name",
        "published",
    ]
    list_filter = [
        "post_type",
    ]
    readonly_fields = [
        "target_object",
        "published",
    ]
    search_fields = [
        "quote",
        "source_url",
        "target_url",
        "hcard__name",
        "hcard__homepage",
    ]

    def get_hcard_name(self, obj):
        if obj.hcard:
            return obj.hcard.name

    get_hcard_name.short_description = _("h-card name")


@admin.register(Webmention)
class WebmentionAdmin(ClickableUrlMixin, QuotableAdmin):
    form = TextAreaForm
    actions = [
        mark_webmention_approved,
        mark_webmention_unapproved,
        mark_webmention_read,
        mark_webmention_unread,
    ]
    list_display = [
        "source_url",
        "target_url",
        "get_hcard_name",
        "has_been_read",
        "validated",
        "approved",
        "published",
        "target_object",
    ]
    list_filter = [
        "has_been_read",
        "validated",
        "approved",
    ] + QuotableAdmin.list_filter
    fieldsets = (
        (
            "Remote source",
            {
                "fields": (
                    "clickable_source_url",
                    "sent_by",
                    "hcard",
                    "quote",
                    "post_type",
                ),
            },
        ),
        (
            "Local target",
            {
                "fields": (
                    "clickable_target_url",
                    "content_type",
                    "object_id",
                    "target_object",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "published",
                    "has_been_read",
                    "approved",
                    "validated",
                    "notes",
                ),
            },
        ),
    )
    readonly_fields = QuotableAdmin.readonly_fields + [
        "content_type",
        "object_id",
        "clickable_source_url",
        "clickable_target_url",
        "sent_by",
    ]


@admin.register(OutgoingWebmentionStatus)
class OutgoingWebmentionStatusAdmin(ClickableUrlMixin, BaseAdmin):
    date_hierarchy = "created_at"
    list_display = [
        "source_url",
        "target_url",
        "successful",
        "created_at",
    ]
    list_filter = [
        "successful",
        "is_awaiting_retry",
    ]
    search_fields = [
        "source_url",
        "target_url",
    ]
    exclude = [
        "source_url",
        "target_url",
    ]
    readonly_fields = [
        "created_at",
        "clickable_source_url",
        "clickable_target_url",
        "target_webmention_endpoint",
        "status_message",
        "response_code",
        "successful",
        *RETRYABLEMIXIN_FIELDS,
    ]


@admin.register(HCard)
class HCardAdmin(BaseAdmin):
    list_display = ["name", "homepage"]
    search_fields = ["name", "homepage"]


@admin.register(PendingIncomingWebmention)
class PendingIncomingAdmin(BaseAdmin):
    list_filter = [
        "is_awaiting_retry",
    ]
    readonly_fields = [
        "created_at",
        "source_url",
        "target_url",
        "sent_by",
        *RETRYABLEMIXIN_FIELDS,
    ]
    search_fields = [
        "source_url",
        "target_url",
    ]


@admin.register(PendingOutgoingContent)
class PendingOutgoingAdmin(BaseAdmin):
    readonly_fields = [
        "created_at",
        "absolute_url",
        "text",
    ]
    search_fields = [
        "absolute_url",
        "text",
    ]


def clickable_link(url: str) -> str:
    return mark_safe(f"<a href={url}>{url}</a>")
