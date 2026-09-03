from rest_framework.permissions import BasePermission

from .rbac import is_super_administrator, user_has_effective_permission


class HasPermission(BasePermission):
    """Require a specific permission based on the user's role.

    Super Administrator always passes. `permission_required` may be a string
    or a list of strings (any match).
    """

    permission_required: str | list[str] = ""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if is_super_administrator(request.user):
            return True
        required = getattr(view, "permission_required", self.permission_required)
        if not required:
            return True
        if isinstance(required, (list, tuple)):
            return any(user_has_effective_permission(request.user, item) for item in required)
        return user_has_effective_permission(request.user, required)
