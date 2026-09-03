import uuid

from django.db import models


class Enquiry(models.Model):
    """Contact / stay enquiry submitted from the website or recorded by staff."""

    class Channel(models.TextChoices):
        WEBSITE = "Website", "Website"
        PHONE = "Phone", "Phone"
        EMAIL = "Email", "Email"

    class Status(models.TextChoices):
        NEW = "New", "New"
        IN_PROGRESS = "In progress", "In progress"
        CLOSED = "Closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=16, unique=True, blank=True)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        default=Channel.WEBSITE,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    received_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_enquiries",
    )
    staff_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-received_at"]
        verbose_name_plural = "enquiries"

    def __str__(self):
        return f"{self.reference or self.id} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            last = (
                Enquiry.objects.filter(reference__startswith="ENQ-")
                .order_by("-reference")
                .values_list("reference", flat=True)
                .first()
            )
            if last:
                try:
                    seq = int(last.split("-", 1)[1]) + 1
                except (IndexError, ValueError):
                    seq = Enquiry.objects.count() + 1
            else:
                seq = 1
            self.reference = f"ENQ-{seq:02d}"
        super().save(*args, **kwargs)
