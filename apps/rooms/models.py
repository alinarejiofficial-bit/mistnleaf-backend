import uuid

from django.db import models


class RoomType(models.Model):
    """Bookable room category — shared by public website and staff dashboard."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    max_guests = models.PositiveSmallIntegerField(default=2)
    beds = models.CharField(max_length=120, blank=True)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    size_label = models.CharField(max_length=32, blank=True, help_text='e.g. "42 m²"')
    size_sq_ft = models.PositiveIntegerField(null=True, blank=True)
    amenities = models.JSONField(default=list, blank=True)
    included_services = models.JSONField(default=list, blank=True)
    policies = models.JSONField(default=list, blank=True)
    availability_note = models.TextField(blank=True)
    image = models.URLField(max_length=500, blank=True)
    gallery = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    @property
    def active_unit_count(self) -> int:
        return self.units.filter(is_active=True).count()


class RoomUnit(models.Model):
    """Physical room inventory — assigned to bookings and housekeeping."""

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        OCCUPIED = "occupied", "Occupied"
        RESERVED = "reserved", "Reserved"
        MAINTENANCE = "maintenance", "Maintenance"
        DIRTY = "dirty", "Dirty"
        CLEANING = "cleaning", "Cleaning"
        READY = "ready", "Ready"

    class HousekeepingStatus(models.TextChoices):
        CLEAN = "clean", "Clean"
        DIRTY = "dirty", "Dirty"
        IN_PROGRESS = "in_progress", "In Progress"
        INSPECTED = "inspected", "Inspected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,
        related_name="units",
    )
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120, blank=True)
    floor = models.CharField(max_length=10, blank=True)
    capacity = models.PositiveSmallIntegerField(default=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    housekeeping_status = models.CharField(
        max_length=20,
        choices=HousekeepingStatus.choices,
        default=HousekeepingStatus.CLEAN,
    )
    notes = models.TextField(blank=True)
    assignee = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["room_type__sort_order", "code"]

    def __str__(self):
        return self.code

    @property
    def display_name(self) -> str:
        return self.name or f"{self.room_type.name} {self.code}"

    def save(self, *args, **kwargs):
        if not self.capacity:
            self.capacity = self.room_type.max_guests
        if not self.name:
            self.name = self.display_name
        super().save(*args, **kwargs)
