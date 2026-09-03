from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    PublicAvailabilityView,
    PublicRoomTypeDetailView,
    PublicRoomTypeListView,
    StaffRoomTypeViewSet,
    StaffRoomUnitViewSet,
)

router = DefaultRouter()
router.register("staff/room-types", StaffRoomTypeViewSet, basename="staff-room-type")
router.register("staff/rooms", StaffRoomUnitViewSet, basename="staff-room")

public_urlpatterns = [
    path("public/room-types/", PublicRoomTypeListView.as_view(), name="public-room-type-list"),
    path(
        "public/room-types/<slug:slug>/",
        PublicRoomTypeDetailView.as_view(),
        name="public-room-type-detail",
    ),
    path("public/availability/", PublicAvailabilityView.as_view(), name="public-availability"),
]

urlpatterns = public_urlpatterns + [path("", include(router.urls))]
