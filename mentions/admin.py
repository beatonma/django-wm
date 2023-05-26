from django import forms
from django.contrib import admin

from mentions.models import (
    HCard,
    OutgoingWebmentionStatus,
    PendingIncomingWebmention,
    PendingOutgoingContent,
    SimpleMention,
    Webmention,
)

RETRYABLEMIXIN_FIELDS = [
    "is_awaiting_retry",
    "last_retry_attempt",
    "retry_attempt_count",
]


@admin.action(permissions=["change"])
def approve_webmention(modeladmin, request, queryset):
    queryset.update(approved=True)


@admin.action(permissions=["change"])
def disapprove_webmention(modeladmin, request, queryset):
    queryset.update(approved=False)


class BaseAdmin(admin.ModelAdmin):
    save_on_top = True


@admin.register(SimpleMention)
class QuotableAdmin(BaseAdmin):
    date_hierarchy = "published"
    list_display = [
        "source_url",
        "target_url",
        "published",
        "hcard",
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


class WebmentionModelForm(forms.ModelForm):
    class Meta:
        model = Webmention
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        fields = "__all__"


@admin.register(Webmention)
class WebmentionAdmin(QuotableAdmin):
    form = WebmentionModelForm
    actions = [
        approve_webmention,
        disapprove_webmention,
    ]
    list_display = [
        "source_url",
        "target_url",
        "hcard",
        "published",
        "validated",
        "approved",
        "target_object",
    ]
    list_filter = ["validated", "approved", "post_type"]
    fieldsets = (
        (
            "Remote source",
            {
                "fields": (
                    "source_url",
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
                    "target_url",
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
    ]


@admin.register(OutgoingWebmentionStatus)
class OutgoingWebmentionStatusAdmin(BaseAdmin):
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
    readonly_fields = [
        "created_at",
        "source_url",
        "target_url",
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
