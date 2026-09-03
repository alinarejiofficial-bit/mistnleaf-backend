from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from apps.accounts.drf_permissions import HasPermission

from .models import MaintenanceTicket
from .serializers import MaintenanceTicketSerializer, MaintenanceTicketWriteSerializer


class StaffMaintenanceTicketViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    pagination_class = None
    http_method_names = ["get", "post", "patch", "head", "options"]
    lookup_field = "reference"
    lookup_url_kwarg = "pk"
    queryset = MaintenanceTicket.objects.select_related("room_unit")

    @property
    def permission_required(self):
        if self.action in ("list", "retrieve"):
            return [
                "manage_maintenance",
                "monitor_maintenance",
                "report_maintenance_issues",
                "update_maintenance_status",
            ]
        if self.action == "create":
            return [
                "manage_maintenance",
                "report_maintenance_issues",
            ]
        return [
            "manage_maintenance",
            "update_maintenance_status",
            "monitor_maintenance",
        ]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return MaintenanceTicketWriteSerializer
        return MaintenanceTicketSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    @extend_schema(
        summary="List maintenance tickets",
        tags=["Staff — Maintenance"],
        parameters=[OpenApiParameter("status", str)],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Create maintenance ticket", tags=["Staff — Maintenance"])
    def create(self, request, *args, **kwargs):
        serializer = MaintenanceTicketWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()
        return Response(MaintenanceTicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Update maintenance ticket", tags=["Staff — Maintenance"])
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = MaintenanceTicketWriteSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(MaintenanceTicketSerializer(instance).data)
