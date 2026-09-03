import uuid

from django.db import models


class MaintenanceTicket(models.Model):
    class Priority(models.TextChoices):
        CRITICAL = "Critical", "Critical"
        HIGH = "High", "High"
        MEDIUM = "Medium", "Medium"
        LOW = "Low", "Low"

    class Status(models.TextChoices):
        OPEN = "Open", "Open"
        IN_PROGRESS = "In progress", "In progress"
        RESOLVED = "Resolved", "Resolved"

    class Category(models.TextChoices):
        PLUMBING = "Plumbing", "Plumbing"
        ELECTRICAL = "Electrical", "Electrical"
        HVAC = "AC / HVAC", "AC / HVAC"
        FURNITURE = "Furniture", "Furniture"
        OTHER = "Other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=16, unique=True, blank=True)
    room_unit = models.ForeignKey(
        "rooms.RoomUnit",
        on_delete=models.CASCADE,
        related_name="maintenance_tickets",
        null=True,
        blank=True,
    )
    room = models.CharField(max_length=120)
    issue = models.CharField(max_length=255)
    category = models.CharField(
        max_length=32,
        choices=Category.choices,
        default=Category.OTHER,
    )
    priority = models.CharField(
        max_length=16,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    reported_by = models.CharField(max_length=120, blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-reported_at"]

    def __str__(self):
        return self.reference or str(self.id)

    def save(self, *args, **kwargs):
        if not self.reference:
            last = (
                MaintenanceTicket.objects.filter(reference__startswith="MT-")
                .order_by("-reference")
                .values_list("reference", flat=True)
                .first()
            )
            if last:
                try:
                    seq = int(last.split("-", 1)[1]) + 1
                except (IndexError, ValueError):
                    seq = MaintenanceTicket.objects.count() + 1
            else:
                seq = 11
            self.reference = f"MT-{seq}"
        if self.room_unit and not self.room:
            self.room = self.room_unit.display_name
        super().save(*args, **kwargs)
