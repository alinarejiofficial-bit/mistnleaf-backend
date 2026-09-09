import base64
import re

from django.core.files.base import ContentFile
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import CmsEditorAuthentication
from .models import CmsMedia
from .permissions import IsCmsEditor

ALLOWED_IMAGE_TYPES = frozenset(
    {"image/jpeg", "image/png", "image/webp", "image/gif", "image/svg+xml"}
)
ALLOWED_VIDEO_TYPES = frozenset(
    {
        "video/mp4",
        "video/webm",
        "video/quicktime",
        "video/x-msvideo",
        "video/ogg",
    }
)
ALLOWED_MEDIA_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_VIDEO_BYTES = 50 * 1024 * 1024


def max_bytes_for(content_type: str) -> int:
    if content_type.startswith("video/"):
        return MAX_VIDEO_BYTES
    return MAX_IMAGE_BYTES


class CmsMediaUploadView(APIView):
    """
    Upload CMS images/videos.

    Accepts multipart file upload or JSON with base64 data URL
    (compatible with admin dashboard ImageUploadField / MediaUrlField).
    """

    authentication_classes = [CmsEditorAuthentication]
    permission_classes = [IsCmsEditor]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(summary="Upload CMS media", tags=["CMS"])
    def post(self, request):
        user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None

        upload_file = request.FILES.get("file")
        if upload_file:
            content_type = (upload_file.content_type or "").lower()
            if content_type not in ALLOWED_MEDIA_TYPES:
                return Response(
                    {
                        "error": (
                            "Unsupported file type. Upload JPEG, PNG, WebP, GIF, SVG, "
                            "or video (MP4, WebM, MOV)."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            limit = max_bytes_for(content_type)
            if upload_file.size > limit:
                mb = limit // (1024 * 1024)
                return Response(
                    {"error": f"File too large. Maximum size is {mb} MB."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            media = CmsMedia.objects.create(
                file=upload_file,
                original_name=upload_file.name,
                content_type=content_type,
                size_bytes=upload_file.size,
                uploaded_by=user,
            )
            return Response(
                {"ok": True, "url": request.build_absolute_uri(media.url), "id": str(media.id)}
            )

        data_url = request.data.get("dataUrl") or request.data.get("image")
        filename = request.data.get("filename") or "upload.png"
        if data_url:
            try:
                match = re.match(
                    r"^data:((?:image|video)/[\w.+-]+);base64,(.+)$",
                    data_url,
                    re.DOTALL,
                )
                if not match:
                    return Response({"error": "Invalid data URL."}, status=status.HTTP_400_BAD_REQUEST)
                content_type, encoded = match.groups()
                content_type = content_type.lower()
                if content_type not in ALLOWED_MEDIA_TYPES:
                    return Response(
                        {"error": "Unsupported media type."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                raw = base64.b64decode(encoded)
                limit = max_bytes_for(content_type)
                if len(raw) > limit:
                    mb = limit // (1024 * 1024)
                    return Response(
                        {"error": f"File too large. Maximum size is {mb} MB."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                media = CmsMedia(
                    original_name=filename,
                    content_type=content_type,
                    size_bytes=len(raw),
                    uploaded_by=user,
                )
                media.file.save(filename, ContentFile(raw), save=False)
                media.save()
                return Response(
                    {"ok": True, "url": request.build_absolute_uri(media.url), "id": str(media.id)}
                )
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid base64 media data."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response({"error": "Provide a file or dataUrl."}, status=status.HTTP_400_BAD_REQUEST)


class CmsMediaListView(APIView):
    authentication_classes = [CmsEditorAuthentication]
    permission_classes = [IsCmsEditor]

    @extend_schema(summary="List CMS media uploads", tags=["CMS"])
    def get(self, request):
        items = CmsMedia.objects.all()[:100]
        return Response(
            {
                "results": [
                    {
                        "id": str(item.id),
                        "url": request.build_absolute_uri(item.url),
                        "originalName": item.original_name,
                        "contentType": item.content_type,
                        "sizeBytes": item.size_bytes,
                        "createdAt": item.created_at.isoformat(),
                    }
                    for item in items
                ]
            }
        )
