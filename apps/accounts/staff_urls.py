from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StaffRoleDetailView, StaffRoleListView, StaffSettingsView, StaffUserViewSet

app_name = "accounts_staff"

router = DefaultRouter()
router.register("staff/users", StaffUserViewSet, basename="staff-user")

urlpatterns = [
    path("staff/roles/", StaffRoleListView.as_view(), name="staff-role-list"),
    path("staff/roles/<str:role_id>/", StaffRoleDetailView.as_view(), name="staff-role-detail"),
    path("staff/settings/", StaffSettingsView.as_view(), name="staff-settings"),
    path("", include(router.urls)),
]
