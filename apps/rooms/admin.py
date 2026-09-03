from django.contrib import admin

from .models import RoomType, RoomUnit


class RoomUnitInline(admin.TabularInline):
    model = RoomUnit
    extra = 0
    fields = ("code", "name", "floor", "status", "housekeeping_status", "is_active")


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "base_rate", "max_guests", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [RoomUnitInline]


@admin.register(RoomUnit)
class RoomUnitAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "room_type",
        "floor",
        "status",
        "housekeeping_status",
        "is_active",
    )
    list_filter = ("status", "housekeeping_status", "room_type", "is_active")
    search_fields = ("code", "name")
