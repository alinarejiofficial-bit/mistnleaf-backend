from django.contrib import admin

from .models import CmsContentStore, CmsMedia


@admin.register(CmsContentStore)
class CmsContentStoreAdmin(admin.ModelAdmin):
    list_display = ("id", "updated_at", "updated_by")
    readonly_fields = ("updated_at",)


@admin.register(CmsMedia)
class CmsMediaAdmin(admin.ModelAdmin):
    list_display = ("original_name", "content_type", "size_bytes", "uploaded_by", "created_at")
    search_fields = ("original_name",)
    readonly_fields = ("created_at",)
