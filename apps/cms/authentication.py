"""CMS editor authentication — JWT staff users and legacy admin dashboard headers."""
from __future__ import annotations

from rest_framework import authentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .permissions import CMS_EDITOR_ROLES


class CmsEditorAuthentication(authentication.BaseAuthentication):
    """
    Accept JWT Bearer tokens or X-Mistnleaf-Role-Id headers from the admin dashboard.
    """

    def authenticate(self, request):
        jwt_auth = JWTAuthentication()
        try:
            result = jwt_auth.authenticate(request)
            if result is not None:
                user, _token = result
                if user.is_superuser or user.role == "super_administrator" or user.role in CMS_EDITOR_ROLES:
                    return user, None
                from apps.accounts.rbac import user_has_effective_permission

                if user_has_effective_permission(user, "manage_website") or user_has_effective_permission(
                    user, "update_website_content"
                ):
                    return user, None
        except Exception:
            pass

        role_id = request.headers.get("X-Mistnleaf-Role-Id")
        if role_id in CMS_EDITOR_ROLES:
            request.cms_editor_role = role_id
            return None, None
        return None
