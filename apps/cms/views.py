from drf_spectacular.utils import extend_schema
from django.db import OperationalError
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import CmsEditorAuthentication
from .permissions import IsCmsEditor
from .services import read_cms_content, read_published_cms_content, write_cms_content


class PublishedCmsView(APIView):
    """Public published CMS snapshot for the website and external consumers."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(summary="Published CMS content", tags=["CMS"])
    def get(self, request):
        published = read_published_cms_content()
        response = Response(published)
        response["Cache-Control"] = "no-store"
        return response


class CmsContentView(APIView):
    """Full CMS document for dashboard editors (GET/PUT)."""

    authentication_classes = [CmsEditorAuthentication]
    permission_classes = [IsCmsEditor]

    @extend_schema(summary="Full CMS content (editors)", tags=["CMS"])
    def get(self, request):
        content = read_cms_content()
        response = Response({"content": content})
        response["Cache-Control"] = "no-store"
        return response

    @extend_schema(summary="Save CMS content (editors)", tags=["CMS"])
    def put(self, request):
        content_payload = request.data.get("content")
        if not content_payload:
            return Response({"error": "Missing content field"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
        try:
            saved = write_cms_content(content_payload, user=user)
        except OperationalError:
            return Response(
                {
                    "error": (
                        "Database is busy. Ensure only one Django server is running on port 3001, "
                        "then try again."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({"ok": True, "content": saved})
