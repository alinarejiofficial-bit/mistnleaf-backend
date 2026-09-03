from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import PropertySettings, RolePermissionOverride, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "full_name",
        "role",
        "department",
        "is_active",
        "is_staff",
        "last_login",
    )
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "username", "first_name", "last_name", "phone")
    ordering = ("-created_at",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Mistnleaf", {"fields": ("phone", "role", "department")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Mistnleaf",
            {"fields": ("email", "phone", "role", "department")},
        ),
    )


@admin.register(RolePermissionOverride)
class RolePermissionOverrideAdmin(admin.ModelAdmin):
    list_display = ("role", "updated_at", "updated_by")


@admin.register(PropertySettings)
class PropertySettingsAdmin(admin.ModelAdmin):
    list_display = ("name", "timezone", "currency", "updated_at")
