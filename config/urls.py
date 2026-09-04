"""
URL configuration for Mistnleaf Resort Management System.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def api_root(_request):
    """Django serves the API only; the public site runs on Next.js :3000."""
    return JsonResponse(
        {
            "service": "mistnleaf-api",
            "public_website": "http://localhost:3000",
            "admin_dashboard": "http://localhost:3002",
            "health": "/api/health/",
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", api_root, name="api-root"),
    # Public customer website is the Next.js app on :3000 — Django :3001 is API only.
    path("api/", include("apps.core.urls")),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/", include("apps.accounts.staff_urls")),
    path("api/", include("apps.rooms.urls")),
    path("api/", include("apps.cms.urls")),
    path("api/", include("apps.enquiries.urls")),
    path("api/", include("apps.bookings.urls")),
    path("api/", include("apps.maintenance.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
