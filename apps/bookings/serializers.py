from django.db import transaction
from rest_framework import serializers

from apps.availability.services import get_availability
from apps.rooms.models import RoomType, RoomUnit

from .models import Booking


def sync_room_unit_from_booking(booking: Booking):
    unit = booking.room_unit
    if not unit:
        return
    if booking.status == Booking.Status.CHECKED_IN:
        unit.status = RoomUnit.Status.OCCUPIED
        unit.save(update_fields=["status", "updated_at"])
    elif booking.status == Booking.Status.CHECKED_OUT:
        unit.status = RoomUnit.Status.DIRTY
        unit.housekeeping_status = RoomUnit.HousekeepingStatus.DIRTY
        unit.save(update_fields=["status", "housekeeping_status", "updated_at"])
    elif booking.status == Booking.Status.CANCELLED:
        if unit.status in (RoomUnit.Status.RESERVED, RoomUnit.Status.OCCUPIED):
            unit.status = RoomUnit.Status.AVAILABLE
            unit.save(update_fields=["status", "updated_at"])
    elif booking.status in (
        Booking.Status.CONFIRMED,
        Booking.Status.PENDING,
        Booking.Status.PENDING_PAYMENT,
        Booking.Status.MODIFIED,
    ):
        if unit.status in (RoomUnit.Status.AVAILABLE, RoomUnit.Status.READY):
            unit.status = RoomUnit.Status.RESERVED
            unit.save(update_fields=["status", "updated_at"])


def assign_available_unit(room_type: RoomType):
    return (
        RoomUnit.objects.filter(
            room_type=room_type,
            is_active=True,
            status__in=[RoomUnit.Status.AVAILABLE, RoomUnit.Status.READY],
        )
        .order_by("code")
        .first()
    )


class PublicBookingCreateSerializer(serializers.Serializer):
    guest = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    room = serializers.CharField(help_text="Room type slug")
    checkIn = serializers.DateField()
    checkOut = serializers.DateField()
    adults = serializers.IntegerField(min_value=1, max_value=6, default=2)
    children = serializers.IntegerField(min_value=0, max_value=6, default=0)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        if attrs["checkOut"] <= attrs["checkIn"]:
            raise serializers.ValidationError({"checkOut": "Check-out must be after check-in."})

        room_type = RoomType.objects.filter(slug=attrs["room"], is_active=True).first()
        if not room_type:
            raise serializers.ValidationError({"room": "Unknown room type."})
        attrs["room_type"] = room_type

        availability = get_availability(
            attrs["checkIn"],
            attrs["checkOut"],
            attrs["adults"] + attrs["children"],
            room_type_slug=attrs["room"],
        )
        if not availability.get("valid"):
            raise serializers.ValidationError({"checkOut": availability.get("message", "Invalid dates.")})
        match = next((item for item in availability.get("results", []) if item["available"]), None)
        if not match:
            raise serializers.ValidationError({"room": "Selected room is not available for these dates."})

        nights = (attrs["checkOut"] - attrs["checkIn"]).days
        attrs["amount"] = room_type.base_rate * nights
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        room_type = validated_data["room_type"]
        nights = (validated_data["checkOut"] - validated_data["checkIn"]).days
        amount = room_type.base_rate * nights
        unit = assign_available_unit(room_type)
        booking = Booking.objects.create(
            guest_name=validated_data["guest"],
            guest_email=validated_data["email"],
            guest_phone=validated_data["phone"],
            room_type=room_type,
            room_unit=unit,
            check_in=validated_data["checkIn"],
            check_out=validated_data["checkOut"],
            adults=validated_data["adults"],
            children=validated_data["children"],
            notes=validated_data.get("notes", ""),
            amount=amount,
            status=Booking.Status.PENDING,
            payment_status=Booking.PaymentStatus.PENDING,
            source=Booking.Source.DIRECT_WEBSITE,
        )
        sync_room_unit_from_booking(booking)
        return booking


class StaffBookingSerializer(serializers.ModelSerializer):
    """Matches mistnleaf_admin Reservation type."""

    id = serializers.CharField(source="reference", read_only=True)
    guest = serializers.CharField(source="guest_name")
    email = serializers.EmailField(source="guest_email")
    phone = serializers.CharField(source="guest_phone")
    room = serializers.SerializerMethodField()
    roomType = serializers.CharField(source="room_type.name")
    roomUnitId = serializers.UUIDField(source="room_unit_id", allow_null=True, read_only=True)
    checkIn = serializers.DateField(source="check_in", format="%Y-%m-%d")
    checkOut = serializers.DateField(source="check_out", format="%Y-%m-%d")
    nights = serializers.IntegerField(read_only=True)
    paymentStatus = serializers.CharField(source="payment_status")
    paymentMethod = serializers.CharField(source="payment_method", required=False, allow_blank=True)
    paidAmount = serializers.DecimalField(source="paid_amount", max_digits=10, decimal_places=2)

    class Meta:
        model = Booking
        fields = (
            "id",
            "guest",
            "email",
            "phone",
            "room",
            "roomType",
            "roomUnitId",
            "adults",
            "children",
            "checkIn",
            "checkOut",
            "nights",
            "status",
            "source",
            "paymentStatus",
            "paymentMethod",
            "amount",
            "paidAmount",
            "notes",
        )

    def get_room(self, obj):
        if obj.room_unit:
            return obj.room_unit.display_name
        return obj.room_type.name


class StaffBookingUpdateSerializer(serializers.ModelSerializer):
    guest = serializers.CharField(source="guest_name", required=False, max_length=120)
    email = serializers.EmailField(source="guest_email", required=False)
    phone = serializers.CharField(source="guest_phone", required=False, max_length=20)
    checkIn = serializers.DateField(source="check_in", required=False)
    checkOut = serializers.DateField(source="check_out", required=False)
    adults = serializers.IntegerField(required=False, min_value=1, max_value=6)
    children = serializers.IntegerField(required=False, min_value=0, max_value=6)
    source = serializers.ChoiceField(choices=Booking.Source.choices, required=False)
    payment_method = serializers.ChoiceField(
        choices=Booking.PaymentMethod.choices,
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Booking
        fields = (
            "status",
            "payment_status",
            "payment_method",
            "paid_amount",
            "room_unit",
            "notes",
            "guest",
            "email",
            "phone",
            "checkIn",
            "checkOut",
            "adults",
            "children",
            "source",
        )

    def validate(self, attrs):
        check_in = attrs.get("check_in", getattr(self.instance, "check_in", None))
        check_out = attrs.get("check_out", getattr(self.instance, "check_out", None))
        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError(
                {"checkOut": "Check-out must be after check-in."}
            )
        return attrs

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        sync_room_unit_from_booking(instance)
        return instance


class StaffBookingCreateSerializer(serializers.Serializer):
    guest = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    room = serializers.CharField(required=False, allow_blank=True)
    roomType = serializers.CharField(required=False, allow_blank=True)
    room_unit = serializers.UUIDField(required=False)
    checkIn = serializers.DateField()
    checkOut = serializers.DateField()
    adults = serializers.IntegerField(min_value=1, max_value=6, default=2)
    children = serializers.IntegerField(min_value=0, max_value=6, default=0)
    source = serializers.ChoiceField(choices=Booking.Source.choices, default=Booking.Source.WALK_IN)
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    status = serializers.ChoiceField(choices=Booking.Status.choices, default=Booking.Status.CONFIRMED)
    paymentStatus = serializers.ChoiceField(
        choices=Booking.PaymentStatus.choices,
        default=Booking.PaymentStatus.PENDING,
        required=False,
    )
    paymentMethod = serializers.ChoiceField(
        choices=Booking.PaymentMethod.choices,
        required=False,
        allow_blank=True,
    )
    paidAmount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    def validate(self, attrs):
        if attrs["checkOut"] <= attrs["checkIn"]:
            raise serializers.ValidationError({"checkOut": "Check-out must be after check-in."})

        room_type = None
        unit = None
        room_unit_id = attrs.get("room_unit")
        if room_unit_id:
            unit = RoomUnit.objects.filter(id=room_unit_id).select_related("room_type").first()
            if unit:
                room_type = unit.room_type

        # Prefer explicit room type (name/slug). `room` used to be sent as a unit label by mistake.
        if not room_type:
            for key in ("roomType", "room"):
                slug_or_name = (attrs.get(key) or "").strip()
                if not slug_or_name:
                    continue
                room_type = (
                    RoomType.objects.filter(slug=slug_or_name).first()
                    or RoomType.objects.filter(name__iexact=slug_or_name).first()
                )
                if room_type:
                    break

        if not room_type:
            raise serializers.ValidationError({"room": "Unknown room type."})
        attrs["room_type"] = room_type

        if unit and unit.room_type_id != room_type.id:
            unit = None
        if not unit and room_unit_id:
            unit = RoomUnit.objects.filter(id=room_unit_id, room_type=room_type).first()
        if not unit:
            unit = assign_available_unit(room_type)
        attrs["unit"] = unit
        nights = (attrs["checkOut"] - attrs["checkIn"]).days
        attrs["amount"] = room_type.base_rate * nights
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        paid = validated_data.get("paidAmount") or 0
        booking = Booking.objects.create(
            guest_name=validated_data["guest"],
            guest_email=validated_data["email"],
            guest_phone=validated_data["phone"],
            room_type=validated_data["room_type"],
            room_unit=validated_data.get("unit"),
            check_in=validated_data["checkIn"],
            check_out=validated_data["checkOut"],
            adults=validated_data["adults"],
            children=validated_data["children"],
            notes=validated_data.get("notes", ""),
            amount=validated_data["amount"],
            paid_amount=paid,
            status=validated_data.get("status") or Booking.Status.CONFIRMED,
            payment_status=validated_data.get("paymentStatus") or Booking.PaymentStatus.PENDING,
            payment_method=validated_data.get("paymentMethod") or "",
            source=validated_data.get("source") or Booking.Source.WALK_IN,
        )
        sync_room_unit_from_booking(booking)
        return booking
