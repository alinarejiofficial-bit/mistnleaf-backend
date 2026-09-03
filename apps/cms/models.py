import uuid

from django.db import models

SINGLETON_PK = uuid.UUID("00000000-0000-0000-0000-000000000001")


class CmsContentStore(models.Model):
    """Singleton document store for website CMS content (matches admin CmsContent JSON)."""

    id = models.UUIDField(primary_key=True, default=SINGLETON_PK, editable=False)
    content = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cms_updates",
    )

    class Meta:
        verbose_name = "CMS content"
        verbose_name_plural = "CMS content"

    def __str__(self):
        return "Website CMS content"

    def save(self, *args, **kwargs):
        self.pk = SINGLETON_PK
        super().save(*args, **kwargs)


def cms_media_upload_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return f"cms/{uuid.uuid4().hex}.{ext}"


class CmsMedia(models.Model):
    """Uploaded CMS image/media asset."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=cms_media_upload_path)
    original_name = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    size_bytes = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cms_media_uploads",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.original_name or str(self.id)

    @property
    def url(self) -> str:
        if self.file:
            return self.file.url
        return ""

