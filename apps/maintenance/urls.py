from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StaffMaintenanceTicketViewSet

app_name = "maintenance"

router = DefaultRouter()
router.register("staff/maintenance", StaffMaintenanceTicketViewSet, basename="staff-maintenance")

urlpatterns = [
    path("", include(router.urls)),
]
