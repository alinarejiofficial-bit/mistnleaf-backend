from drf_spectacular.utils import OpenApiParameter, extend_schema
from django.db.models import Q
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response

from apps.accounts.drf_permissions import HasPermission

from .models import Booking
from .serializers import (
    PublicBookingCreateSerializer,
    StaffBookingCreateSerializer,
    StaffBookingSerializer,
    StaffBookingUpdateSerializer,
)


class PublicBookingCreateView(generics.CreateAPIView):
    """Create a booking request from the public website booking flow."""

    serializer_class = PublicBookingCreateSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(summary="Create booking (public)", tags=["Public — Bookings"])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(
            {
                "ok": True,
                "id": booking.reference,
                "status": booking.status,
                "amount": str(booking.amount),
                "message": "Booking request received. Complete payment to confirm your stay.",
            },
            status=status.HTTP_201_CREATED,
        )


class StaffBookingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    http_method_names = ["get", "post", "patch", "head", "options"]
    lookup_field = "reference"
    lookup_url_kwarg = "pk"
    pagination_class = None

    @property
    def permission_required(self):
        if self.action in ("list", "retrieve"):
            return [
                "manage_bookings",
                "create_bookings",
                "modify_bookings",
                "check_guests_in",
                "check_guests_out",
                "manage_check_in_out",
                "view_payments",
                "view_revenue",
                "view_reports",
                "generate_financial_reports",
                "view_outstanding_balances",
            ]
        return [
            "manage_bookings",
            "create_bookings",
            "modify_bookings",
            "check_guests_in",
            "check_guests_out",
            "confirm_bookings",
            "cancel_bookings",
            "record_payments",
            "record_offline_payments",
            "assign_rooms",
        ]

    def get_queryset(self):
        qs = Booking.objects.select_related("room_type", "room_unit")
        status_filter = self.request.query_params.get("status")
        source = self.request.query_params.get("source")
        search = self.request.query_params.get("search", "").strip()
        if status_filter:
            qs = qs.filter(status=status_filter)
        if source:
            qs = qs.filter(source=source)
        if search:
            qs = qs.filter(
                Q(guest_name__icontains=search)
                | Q(guest_email__icontains=search)
                | Q(reference__icontains=search)
            )
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return StaffBookingCreateSerializer
        if self.action in ("partial_update", "update"):
            return StaffBookingUpdateSerializer
        return StaffBookingSerializer

    @extend_schema(
        summary="List bookings",
        tags=["Staff — Bookings"],
        parameters=[
            OpenApiParameter("status", str),
            OpenApiParameter("source", str),
            OpenApiParameter("search", str),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Get booking", tags=["Staff — Bookings"])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Create booking", tags=["Staff — Bookings"])
    def create(self, request, *args, **kwargs):
        serializer = StaffBookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(StaffBookingSerializer(booking).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Update booking", tags=["Staff — Bookings"])
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = StaffBookingUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(StaffBookingSerializer(instance).data)
