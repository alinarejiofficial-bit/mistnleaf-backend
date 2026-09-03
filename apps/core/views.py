from django.db import connection
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Public health-check endpoint for load balancers and monitoring."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Health check",
        description="Returns service status and database connectivity.",
        tags=["System"],
    )
    def get(self, request):
        db_status = "ok"
        try:
            connection.ensure_connection()
        except Exception:
            db_status = "error"

        overall_status = "healthy" if db_status == "ok" else "degraded"
        http_status = (
            status.HTTP_200_OK
            if overall_status == "healthy"
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return Response(
            {
                "status": overall_status,
                "service": "mistnleaf-backend",
                "database": db_status,
                "timestamp": timezone.now().isoformat(),
            },
            status=http_status,
        )
