from django.contrib import admin

from .models import HCard, SimpleMention, Webmention


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
    readonly_fields = ['target_object', ]
    actions = [
        approve_webmention,
        disapprove_webmention,
    ]
    list_display = [
        'source_url',
        'validated',
        'approved',
        'content_type',
    ]
    date_hierarchy = 'created'
    fieldsets = (
        ('Remote source', {
            'fields': (
                'source_url',
                'sent_by',
                'hcard',
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
                'approved',
                'validated',
                'notes',
            ),
        })
    )


@admin.register(HCard)
class HCardAdmin(BaseAdmin):
    list_display = ['name', 'homepage']
    search_fields = ['name', 'homepage']
