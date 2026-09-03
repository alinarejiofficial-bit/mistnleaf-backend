from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EnquiryStatsView, PublicEnquiryCreateView, StaffEnquiryViewSet

app_name = "enquiries"

router = DefaultRouter()
router.register(r"staff/enquiries", StaffEnquiryViewSet, basename="staff-enquiry")

urlpatterns = [
    path("public/enquiries/", PublicEnquiryCreateView.as_view(), name="public-enquiry-create"),
    path("staff/enquiries/stats/", EnquiryStatsView.as_view(), name="staff-enquiry-stats"),
    path("", include(router.urls)),
]
