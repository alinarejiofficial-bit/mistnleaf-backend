"""
RBAC helpers for Super Administrator and lower staff roles.

Uses the existing role/permission matrix — does not introduce a second system.
"""
from __future__ import annotations

from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import RolePermissionOverride, User
from .permissions import (
    LOCKED_ROLE_ID,
    PERMISSIONS,
    ROLE_PERMISSIONS,
    SYSTEM_LEVEL_PERMISSIONS,
    SUPER_ADMINISTRATOR_PERMISSIONS,
    base_permissions_for_role,
)


def is_super_administrator(user) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    return bool(getattr(user, "is_super_administrator", False) or getattr(user, "is_superuser", False))


def effective_permissions(role_id: str) -> list[str]:
    if role_id == LOCKED_ROLE_ID:
        return list(SUPER_ADMINISTRATOR_PERMISSIONS)

    base = set(base_permissions_for_role(role_id))
    override = RolePermissionOverride.objects.filter(role=role_id).first()
    if override:
        base |= {item for item in (override.granted or []) if item in PERMISSIONS}
        base -= set(override.revoked or [])
    base -= SYSTEM_LEVEL_PERMISSIONS
    return sorted(base)


def user_has_effective_permission(user, permission: str) -> bool:
    if is_super_administrator(user):
        return True
    role_id = getattr(user, "role", "")
    return permission in effective_permissions(role_id)


def apply_super_admin_flags(user: User, role_id: str) -> None:
    if role_id == LOCKED_ROLE_ID:
        user.is_superuser = True
        user.is_staff = True
    else:
        user.is_superuser = False


def active_super_admin_qs(exclude_id=None):
    qs = User.objects.filter(role=LOCKED_ROLE_ID, is_active=True)
    if exclude_id is not None:
        qs = qs.exclude(pk=exclude_id)
    return qs


def can_assign_role(actor, role_id: str) -> bool:
    if role_id not in ROLE_PERMISSIONS:
        return False
    if is_super_administrator(actor):
        return True
    if user_has_effective_permission(actor, "manage_staff"):
        return role_id != LOCKED_ROLE_ID
    return False


def assert_can_assign_role(actor, role_id: str) -> None:
    if role_id not in ROLE_PERMISSIONS:
        raise ValidationError({"role_id": "Unknown role."})
    if not can_assign_role(actor, role_id):
        raise PermissionDenied("You cannot assign the Super Administrator role.")


def assert_can_manage_target(actor, target: User, *, deleting=False) -> None:
    if actor.pk == target.pk:
        raise PermissionDenied("You cannot change your own account from this screen.")

    if is_super_administrator(target) and not is_super_administrator(actor):
        raise PermissionDenied(
            "Super Administrator accounts cannot be modified by lower-level roles."
        )

    if deleting and not user_has_effective_permission(actor, "manage_users"):
        raise PermissionDenied("Only Super Administrators can delete users.")

    if not is_super_administrator(actor) and not user_has_effective_permission(actor, "manage_staff"):
        if not user_has_effective_permission(actor, "manage_users"):
            raise PermissionDenied("You do not have permission to manage this user.")


def assert_not_last_super_admin(target: User, next_role: str | None = None, next_active: bool | None = None) -> None:
    remaining = active_super_admin_qs(exclude_id=target.pk).count()
    still_super = (next_role or target.role) == LOCKED_ROLE_ID
    still_active = target.is_active if next_active is None else next_active
    if remaining == 0 and (not still_super or not still_active):
        raise ValidationError(
            {"role_id": "The last Super Administrator cannot be removed, demoted, or deactivated."}
        )


def save_role_permissions(role_id: str, selected: list[str], actor) -> RolePermissionOverride:
    if role_id == LOCKED_ROLE_ID:
        raise PermissionDenied("Super Administrator permissions cannot be modified.")
    if role_id not in ROLE_PERMISSIONS:
        raise ValidationError({"role": "Unknown role."})

    selected_set = {item for item in selected if item in PERMISSIONS} - SYSTEM_LEVEL_PERMISSIONS
    base = set(base_permissions_for_role(role_id))
    granted = sorted(selected_set - base)
    revoked = sorted(base - selected_set)
    override, _created = RolePermissionOverride.objects.update_or_create(
        role=role_id,
        defaults={"granted": granted, "revoked": revoked, "updated_by": actor},
    )
    return override
