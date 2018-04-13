from django.contrib import admin

from .models import HCard, Webmention


def approve_webmention(modeladmin, request, queryset):
    queryset.update(approved=True)


def disapprove_webmention(modeladmin, request, queryset):
    queryset.update(approved=False)


class BaseAdmin(admin.ModelAdmin):
    save_on_top = True


@admin.register(Webmention)
class WebmentionAdmin(BaseAdmin):
    actions = [
        approve_webmention,
        disapprove_webmention,
    ]
    list_display = ['source', 'target', 'validated', 'approved']
    search_fields = ['source', 'target']
    date_hierarchy = 'created'
    fieldsets = (
        ('Remote source', {
            'fields': (
                'source',
                'sent_by',
                'hcard_homepage'
            ),
        }),
        ('Local target', {
            'fields': (
                'target',
                'target_slug'
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
