from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.drf_permissions import HasPermission

from .models import Enquiry
from .serializers import (
    PublicEnquiryCreateSerializer,
    StaffEnquirySerializer,
    StaffEnquiryUpdateSerializer,
)


class PublicEnquiryCreateView(generics.CreateAPIView):
    """Submit a contact / stay enquiry from the public website."""

    serializer_class = PublicEnquiryCreateSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Submit enquiry (public)",
        tags=["Public — Enquiries"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enquiry = serializer.save()
        return Response(
            {
                "ok": True,
                "id": enquiry.reference,
                "message": "Thank you — we received your enquiry and will respond shortly.",
            },
            status=status.HTTP_201_CREATED,
        )


class StaffEnquiryViewSet(viewsets.ModelViewSet):
    """Staff enquiry inbox — list, retrieve, update status."""

    permission_classes = [HasPermission]
    permission_required = "manage_enquiries"
    http_method_names = ["get", "patch", "head", "options"]
    lookup_field = "reference"
    lookup_url_kwarg = "pk"
    pagination_class = None

    def get_queryset(self):
        qs = Enquiry.objects.all()
        status_filter = self.request.query_params.get("status")
        channel = self.request.query_params.get("channel")
        search = self.request.query_params.get("search", "").strip()
        if status_filter:
            qs = qs.filter(status=status_filter)
        if channel:
            qs = qs.filter(channel=channel)
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(email__icontains=search)
                | Q(subject__icontains=search)
            )
        return qs

    def get_serializer_class(self):
        if self.action in ("partial_update", "update"):
            return StaffEnquiryUpdateSerializer
        return StaffEnquirySerializer

    @extend_schema(
        summary="List enquiries",
        tags=["Staff — Enquiries"],
        parameters=[
            OpenApiParameter("status", str, description="Filter by status"),
            OpenApiParameter("channel", str, description="Filter by channel"),
            OpenApiParameter("search", str, description="Search name, email, subject"),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Get enquiry", tags=["Staff — Enquiries"])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Update enquiry status/notes", tags=["Staff — Enquiries"])
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = StaffEnquiryUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(StaffEnquirySerializer(instance).data)


class EnquiryStatsView(APIView):
    """Quick counts for dashboard widgets."""

    permission_classes = [HasPermission]
    permission_required = "manage_enquiries"

    @extend_schema(summary="Enquiry stats", tags=["Staff — Enquiries"])
    def get(self, request):
        return Response(
            {
                "total": Enquiry.objects.count(),
                "new": Enquiry.objects.filter(status=Enquiry.Status.NEW).count(),
                "inProgress": Enquiry.objects.filter(status=Enquiry.Status.IN_PROGRESS).count(),
                "closed": Enquiry.objects.filter(status=Enquiry.Status.CLOSED).count(),
            }
        )
