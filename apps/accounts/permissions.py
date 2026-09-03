"""
Permission constants and role-to-permission mappings.

Mirrors the admin frontend matrix in mistnleaf_admin/src/lib/roles.ts
"""
from typing import Final

# All granular permissions used by the admin dashboard
PERMISSIONS: Final[frozenset[str]] = frozenset(
    {
        "manage_settings",
        "manage_users",
        "manage_roles",
        "manage_integrations",
        "view_audit_logs",
        "manage_rooms",
        "manage_bookings",
        "cancel_bookings",
        "confirm_bookings",
        "assign_rooms",
        "export_bookings",
        "export_payments",
        "export_reports",
        "record_operational_payments",
        "update_maintenance_status",
        "manage_calendar",
        "manage_guests",
        "manage_payments",
        "manage_reports",
        "manage_website",
        "manage_pricing",
        "manage_offers",
        "manage_addons",
        "manage_notifications",
        "manage_enquiries",
        "manage_housekeeping",
        "manage_maintenance",
        "monitor_maintenance",
        "view_notifications",
        "manage_staff",
        "view_operational_audit_logs",
        "view_limited_settings",
        "view_operational_data",
        "view_dashboard",
        "manage_check_in_out",
        "view_revenue",
        "view_reports",
        "monitor_housekeeping",
        "create_bookings",
        "modify_bookings",
        "view_availability",
        "register_guests",
        "check_guests_in",
        "check_guests_out",
        "record_payments",
        "generate_invoices",
        "download_invoices",
        "view_room_status",
        "view_assigned_rooms",
        "view_rooms_requiring_cleaning",
        "update_cleaning_status",
        "mark_rooms_ready",
        "report_maintenance_issues",
        "view_payments",
        "record_offline_payments",
        "manage_invoices",
        "view_revenue_reports",
        "view_outstanding_balances",
        "generate_financial_reports",
        "update_website_content",
        "manage_images",
        "manage_room_descriptions",
        "manage_facilities",
        "manage_blog_content",
    }
)

SUPER_ADMINISTRATOR_PERMISSIONS: Final[list[str]] = sorted(PERMISSIONS)

RESORT_MANAGER_PERMISSIONS: Final[list[str]] = sorted(
    {
        "view_dashboard",
        "manage_bookings",
        "create_bookings",
        "modify_bookings",
        "cancel_bookings",
        "confirm_bookings",
        "assign_rooms",
        "export_bookings",
        "manage_calendar",
        "manage_guests",
        "register_guests",
        "manage_check_in_out",
        "check_guests_in",
        "check_guests_out",
        "manage_enquiries",
        "manage_rooms",
        "view_availability",
        "view_room_status",
        "manage_housekeeping",
        "monitor_housekeeping",
        "manage_maintenance",
        "monitor_maintenance",
        "manage_payments",
        "record_payments",
        "record_offline_payments",
        "record_operational_payments",
        "manage_invoices",
        "generate_invoices",
        "download_invoices",
        "view_outstanding_balances",
        "manage_pricing",
        "manage_offers",
        "manage_addons",
        "manage_reports",
        "view_reports",
        "view_revenue",
        "view_revenue_reports",
        "export_reports",
        "export_payments",
        "view_notifications",
        "manage_notifications",
        "manage_staff",
        "view_operational_audit_logs",
        "view_limited_settings",
        "view_operational_data",
        "update_website_content",
    }
)

FRONT_DESK_PERMISSIONS: Final[list[str]] = sorted(
    {
        "view_dashboard",
        "create_bookings",
        "modify_bookings",
        "cancel_bookings",
        "confirm_bookings",
        "assign_rooms",
        "view_availability",
        "manage_calendar",
        "manage_guests",
        "register_guests",
        "manage_check_in_out",
        "check_guests_in",
        "check_guests_out",
        "view_payments",
        "record_payments",
        "record_offline_payments",
        "view_outstanding_balances",
        "manage_invoices",
        "generate_invoices",
        "download_invoices",
        "manage_enquiries",
        "view_notifications",
        "view_room_status",
    }
)

HOUSEKEEPING_PERMISSIONS: Final[list[str]] = sorted(
    {
        "view_dashboard",
        "view_assigned_rooms",
        "view_rooms_requiring_cleaning",
        "update_cleaning_status",
        "mark_rooms_ready",
        "report_maintenance_issues",
        "view_notifications",
    }
)

ACCOUNTANT_PERMISSIONS: Final[list[str]] = sorted(
    {
        "view_dashboard",
        "view_payments",
        "record_payments",
        "record_offline_payments",
        "manage_invoices",
        "generate_invoices",
        "download_invoices",
        "view_outstanding_balances",
        "view_revenue",
        "view_revenue_reports",
        "generate_financial_reports",
        "export_payments",
        "export_reports",
        "view_reports",
        "view_notifications",
    }
)

WEBSITE_CONTENT_MANAGER_PERMISSIONS: Final[list[str]] = sorted(
    {
        "view_dashboard",
        "manage_website",
        "update_website_content",
        "manage_images",
        "manage_room_descriptions",
        "manage_facilities",
        "manage_blog_content",
        "view_notifications",
    }
)

ROLE_PERMISSIONS: Final[dict[str, list[str]]] = {
    "super_administrator": SUPER_ADMINISTRATOR_PERMISSIONS,
    "resort_manager": RESORT_MANAGER_PERMISSIONS,
    "front_desk": FRONT_DESK_PERMISSIONS,
    "housekeeping": HOUSEKEEPING_PERMISSIONS,
    "accountant": ACCOUNTANT_PERMISSIONS,
    "website_content_manager": WEBSITE_CONTENT_MANAGER_PERMISSIONS,
}

ROLE_LABELS: Final[dict[str, str]] = {
    "super_administrator": "Super Administrator",
    "resort_manager": "Resort Manager",
    "front_desk": "Front Desk / Reception",
    "housekeeping": "Housekeeping Staff",
    "accountant": "Accountant / Finance User",
    "website_content_manager": "Website Content Manager",
}

ROLE_DESCRIPTIONS: Final[dict[str, str]] = {
    "super_administrator": (
        "Highest-level system role with complete control over every CMS module, "
        "user, role, permission, and system setting."
    ),
    "resort_manager": "Management-level operational access across the property.",
    "front_desk": "Guest-facing reception focused on bookings, guests, check-in/out, and payments.",
    "housekeeping": "Assigned room cleaning, status updates, readiness, and maintenance reporting.",
    "accountant": "Payments, invoices, and financial reporting across the property.",
    "website_content_manager": "Website content and digital assets for the public MistnLeaf site.",
}

LOCKED_ROLE_ID: Final[str] = "super_administrator"

# Permissions that only Super Administrator may hold. Lower roles cannot receive these
# even if a Super Administrator attempts to grant them.
SYSTEM_LEVEL_PERMISSIONS: Final[frozenset[str]] = frozenset(
    {
        "manage_settings",
        "manage_users",
        "manage_roles",
        "manage_integrations",
        "view_audit_logs",
    }
)


def base_permissions_for_role(role_id: str) -> list[str]:
    if role_id == LOCKED_ROLE_ID:
        return list(SUPER_ADMINISTRATOR_PERMISSIONS)
    return list(ROLE_PERMISSIONS.get(role_id, []))


def get_permissions_for_role(role_id: str) -> list[str]:
    """Static defaults. Prefer rbac.effective_permissions when overrides may apply."""
    return base_permissions_for_role(role_id)


def user_has_permission(role_id: str, permission: str) -> bool:
    return permission in get_permissions_for_role(role_id)
