import uuid
from decimal import Decimal

from django.db import models


class Booking(models.Model):
    """
    Booking record for availability checks and the guest booking flow.
    """

    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        PENDING_PAYMENT = "pending_payment", "Pending Payment"
        CONFIRMED = "Confirmed", "Confirmed"
        CHECKED_IN = "Checked-in", "Checked In"
        CHECKED_OUT = "Checked-out", "Checked Out"
        CANCELLED = "Cancelled", "Cancelled"
        MODIFIED = "modified", "Modified"

    class Source(models.TextChoices):
        DIRECT_WEBSITE = "Direct website", "Direct website"
        OTA = "OTA / Booking.com", "OTA / Booking.com"
        WALK_IN = "Walk-in", "Walk-in"
        TRAVEL_AGENT = "Travel agent", "Travel agent"

    class PaymentStatus(models.TextChoices):
        PAID = "Paid", "Paid"
        PARTIAL = "Partial", "Partial"
        PENDING = "Pending", "Pending"
        REFUNDED = "Refunded", "Refunded"

    class PaymentMethod(models.TextChoices):
        UPI = "UPI", "UPI"
        CARD = "Card", "Card"
        CASH = "Cash", "Cash"
        BANK_TRANSFER = "Bank transfer", "Bank transfer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=32, unique=True, blank=True)
    guest_name = models.CharField(max_length=120, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)
    room_type = models.ForeignKey(
        "rooms.RoomType",
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    room_unit = models.ForeignKey(
        "rooms.RoomUnit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
    )
    check_in = models.DateField()
    check_out = models.DateField()
    adults = models.PositiveSmallIntegerField(default=1)
    children = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    source = models.CharField(
        max_length=32,
        choices=Source.choices,
        default=Source.DIRECT_WEBSITE,
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        blank=True,
        default="",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.reference or str(self.id)

    @property
    def nights(self) -> int:
        if self.check_out < self.check_in:
            return 0
        return max((self.check_out - self.check_in).days, 1)

    @classmethod
    def blocking_statuses(cls):
        return [
            cls.Status.PENDING,
            cls.Status.PENDING_PAYMENT,
            cls.Status.CONFIRMED,
            cls.Status.CHECKED_IN,
            cls.Status.MODIFIED,
        ]

    def save(self, *args, **kwargs):
        if not self.reference:
            last = (
                Booking.objects.filter(reference__startswith="RSV-")
                .order_by("-reference")
                .values_list("reference", flat=True)
                .first()
            )
            if last:
                try:
                    seq = int(last.split("-", 1)[1]) + 1
                except (IndexError, ValueError):
                    seq = Booking.objects.count() + 1
            else:
                seq = 2041
            self.reference = f"RSV-{seq}"
        super().save(*args, **kwargs)
