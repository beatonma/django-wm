from django.contrib import admin

from .models import (
    HCard,
    SimpleMention,
    Webmention,
    OutgoingWebmentionStatus,
)


def approve_webmention(modeladmin, request, queryset):
    queryset.update(approved=True)


def disapprove_webmention(modeladmin, request, queryset):
    queryset.update(approved=False)


class BaseAdmin(admin.ModelAdmin):
    save_on_top = True


@admin.register(SimpleMention)
class QuotableAdmin(BaseAdmin):
    list_display = [
        'source_url',
        'target_url',
        'hcard',
    ]
    search_fields = [
        'source_url',
        'target_url',
        'hcard',
    ]
    date_hierarchy = 'published'


@admin.register(Webmention)
class WebmentionAdmin(QuotableAdmin):
    readonly_fields = ['target_object', 'published', ]
    actions = [
        approve_webmention,
        disapprove_webmention,
    ]
    list_display = [
        'source_url',
        'target_url',
        'published',
        'validated',
        'approved',
        'content_type',
    ]
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Remote source', {
            'fields': (
                'source_url',
                'sent_by',
                'hcard',
                'quote',
            ),
        }),
        ('Local target', {
            'fields': (
                'target_url',
                'content_type',
                'object_id',
                'target_object',
            ),
        }),
        ('Metadata', {
            'fields': (
                'published',
                'approved',
                'validated',
                'notes',
            ),
        })
    )


@admin.register(OutgoingWebmentionStatus)
class OutgoingWebmentionStatusAdmin(BaseAdmin):
    readonly_fields = [
        'created_at',
        'source_url',
        'target_url',
        'target_webmention_endpoint',
        'status_message',
        'response_code',
        'successful',
    ]
    list_display = [
        'source_url',
        'target_url',
        'successful',
        'created_at',
    ]
    date_hierarchy = 'created_at'


@admin.register(HCard)
class HCardAdmin(BaseAdmin):
    list_display = ['name', 'homepage']
    search_fields = ['name', 'homepage']
