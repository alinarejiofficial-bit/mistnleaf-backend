import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Staff user for Mistnleaf Resort Management System."""

    class Role(models.TextChoices):
        SUPER_ADMINISTRATOR = "super_administrator", "Super Administrator"
        RESORT_MANAGER = "resort_manager", "Resort Manager"
        FRONT_DESK = "front_desk", "Front Desk / Reception"
        HOUSEKEEPING = "housekeeping", "Housekeeping Staff"
        ACCOUNTANT = "accountant", "Accountant / Finance User"
        WEBSITE_CONTENT_MANAGER = (
            "website_content_manager",
            "Website Content Manager",
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.FRONT_DESK,
    )
    department = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-created_at"]

    @property
    def full_name(self) -> str:
        return self.get_full_name().strip() or self.email

    @property
    def is_super_administrator(self) -> bool:
        return self.role == self.Role.SUPER_ADMINISTRATOR or self.is_superuser

    def __str__(self):
        return self.email


class RolePermissionOverride(models.Model):
    """Super Administrator grants/revokes on the six built-in roles (not Super Admin)."""

    role = models.CharField(max_length=32, unique=True)
    granted = models.JSONField(default=list, blank=True)
    revoked = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="role_permission_updates",
    )

    class Meta:
        verbose_name = "role permission override"
        verbose_name_plural = "role permission overrides"

    def __str__(self):
        return self.role


class PropertySettings(models.Model):
    """Singleton property / system configuration."""

    singleton_key = models.CharField(max_length=16, unique=True, default="default")
    name = models.CharField(max_length=120, default="MistnLeaf Resort")
    timezone = models.CharField(max_length=64, default="Asia/Kolkata")
    currency = models.CharField(max_length=8, default="INR")
    check_in_time = models.CharField(max_length=8, default="14:00")
    check_out_time = models.CharField(max_length=8, default="11:00")
    tax_percent = models.CharField(max_length=8, default="12")
    extra = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "property settings"
        verbose_name_plural = "property settings"

    def __str__(self):
        return self.name

    @classmethod
    def load(cls) -> "PropertySettings":
        obj, _created = cls.objects.get_or_create(singleton_key="default")
        return obj
