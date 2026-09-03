from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PublicBookingCreateView, StaffBookingViewSet

app_name = "bookings"

router = DefaultRouter()
router.register(r"staff/bookings", StaffBookingViewSet, basename="staff-booking")

urlpatterns = [
    path("public/bookings/", PublicBookingCreateView.as_view(), name="public-booking-create"),
    path("", include(router.urls)),
]
