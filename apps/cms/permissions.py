"""CMS editor authentication — compatible with admin dashboard headers and JWT."""
from __future__ import annotations

from rest_framework.permissions import BasePermission

CMS_EDITOR_ROLES = frozenset({"super_administrator", "website_content_manager"})


def get_editor_role_from_request(request) -> str | None:
    legacy_role = getattr(request, "cms_editor_role", None)
    if legacy_role in CMS_EDITOR_ROLES:
        return legacy_role

    role_id = request.headers.get("X-Mistnleaf-Role-Id")
    if role_id in CMS_EDITOR_ROLES:
        return role_id

    # Read _user directly — never use request.user here (causes auth recursion).
    user = getattr(request, "_user", None)
    if user and getattr(user, "is_authenticated", False):
        if getattr(user, "is_superuser", False) or getattr(user, "role", "") == "super_administrator":
            return "super_administrator"
        if user.role in CMS_EDITOR_ROLES:
            return user.role
        try:
            from apps.accounts.rbac import user_has_effective_permission

            if user_has_effective_permission(user, "manage_website") or user_has_effective_permission(
                user, "update_website_content"
            ):
                return user.role
        except Exception:
            pass
    return None


def can_edit_cms_content(role_id: str | None) -> bool:
    return role_id in CMS_EDITOR_ROLES


class IsCmsEditor(BasePermission):
    def has_permission(self, request, view):
        return bool(get_editor_role_from_request(request))
