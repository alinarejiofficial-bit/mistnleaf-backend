from datetime import datetime

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.drf_permissions import HasPermission
from apps.availability.services import get_availability

from .models import RoomType, RoomUnit
from .serializers import (
    PublicRoomTypeSerializer,
    RoomUnitSerializer,
    RoomUnitStatusSerializer,
    RoomUnitWriteSerializer,
    StaffRoomTypeSerializer,
    StaffRoomTypeWriteSerializer,
)


class PublicRoomTypeListView(generics.ListAPIView):
    """List bookable room types for the public website."""

    serializer_class = PublicRoomTypeSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    pagination_class = None

    def get_queryset(self):
        return RoomType.objects.filter(is_active=True)


class PublicRoomTypeDetailView(generics.RetrieveAPIView):
    """Room type detail for public website pages (/rooms/[slug])."""

    serializer_class = PublicRoomTypeSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    lookup_field = "slug"
    queryset = RoomType.objects.filter(is_active=True)


class PublicAvailabilityView(APIView):
    """
    Check room availability for guest booking flow.

    Used by: public website steps 1–2 (search → availability).
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Check availability",
        description="Returns availability per room type for the given stay dates.",
        tags=["Public — Booking"],
        parameters=[
            OpenApiParameter("checkIn", str, description="Check-in date (YYYY-MM-DD)"),
            OpenApiParameter("checkOut", str, description="Check-out date (YYYY-MM-DD)"),
            OpenApiParameter("guests", int, description="Number of guests"),
            OpenApiParameter("room", str, description="Optional room type slug filter"),
        ],
    )
    def get(self, request):
        check_in_str = request.query_params.get("checkIn") or request.query_params.get("check_in")
        check_out_str = request.query_params.get("checkOut") or request.query_params.get("check_out")
        guests = int(request.query_params.get("guests", 2))
        room_slug = request.query_params.get("room") or request.query_params.get("roomTypeSlug")

        if not check_in_str or not check_out_str:
            return Response(
                {"detail": "checkIn and checkOut query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Dates must be in YYYY-MM-DD format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = get_availability(check_in, check_out, guests, room_slug)
        http_status = status.HTTP_200_OK if data["valid"] else status.HTTP_400_BAD_REQUEST
        return Response(data, status=http_status)


class StaffRoomTypeViewSet(viewsets.ModelViewSet):
    """Staff CRUD for room types — admin dashboard."""

    queryset = RoomType.objects.all()
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    pagination_class = None
    lookup_field = "slug"

    @property
    def permission_required(self):
        if self.action in ("list", "retrieve"):
            return [
                "manage_rooms",
                "view_room_status",
                "view_assigned_rooms",
                "view_availability",
                "assign_rooms",
            ]
        return "manage_rooms"

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return StaffRoomTypeWriteSerializer
        return StaffRoomTypeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            StaffRoomTypeSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(StaffRoomTypeSerializer(self.get_object()).data)


class StaffRoomUnitViewSet(viewsets.ModelViewSet):
    """Staff CRUD for physical room inventory."""

    queryset = RoomUnit.objects.select_related("room_type").prefetch_related("bookings")
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    pagination_class = None

    @property
    def permission_required(self):
        if self.action in ("list", "retrieve"):
            return [
                "view_room_status",
                "view_assigned_rooms",
                "view_rooms_requiring_cleaning",
                "manage_rooms",
                "manage_housekeeping",
                "monitor_housekeeping",
                "assign_rooms",
                "view_payments",
                "view_revenue",
                "view_reports",
                "view_outstanding_balances",
                "generate_financial_reports",
            ]
        if self.action == "update_status":
            return [
                "update_cleaning_status",
                "mark_rooms_ready",
                "manage_rooms",
                "manage_housekeeping",
                "update_maintenance_status",
            ]
        return "manage_rooms"

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return RoomUnitWriteSerializer
        if self.action == "update_status":
            return RoomUnitStatusSerializer
        return RoomUnitSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            RoomUnitSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(RoomUnitSerializer(self.get_object()).data)

    def get_queryset(self):
        qs = super().get_queryset()
        room_type = self.request.query_params.get("room_type")
        status_filter = self.request.query_params.get("status")
        if room_type:
            qs = qs.filter(room_type_id=room_type)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    @extend_schema(summary="Update room operational status", tags=["Staff — Rooms"])
    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        unit = self.get_object()
        serializer = RoomUnitStatusSerializer(unit, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(RoomUnitSerializer(unit).data)
