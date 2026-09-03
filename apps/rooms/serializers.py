from rest_framework import serializers

from .models import RoomType, RoomUnit


class PublicRoomTypeSerializer(serializers.ModelSerializer):
    """Marketing view for the public website (matches site.ts Room shape)."""

    price = serializers.DecimalField(source="base_rate", max_digits=10, decimal_places=2)
    guests = serializers.IntegerField(source="max_guests")
    short = serializers.CharField(source="short_description")
    size = serializers.CharField(source="size_label")
    includedServices = serializers.ListField(source="included_services")
    availability = serializers.CharField(source="availability_note")
    image = serializers.URLField()
    gallery = serializers.ListField()

    class Meta:
        model = RoomType
        fields = (
            "id",
            "slug",
            "name",
            "short",
            "description",
            "price",
            "guests",
            "size",
            "beds",
            "amenities",
            "includedServices",
            "availability",
            "policies",
            "image",
            "gallery",
        )


STATUS_TO_DASHBOARD = {
    RoomUnit.Status.AVAILABLE: "Available",
    RoomUnit.Status.READY: "Available",
    RoomUnit.Status.OCCUPIED: "Occupied",
    RoomUnit.Status.RESERVED: "Reserved",
    RoomUnit.Status.DIRTY: "Cleaning",
    RoomUnit.Status.CLEANING: "Cleaning",
    RoomUnit.Status.MAINTENANCE: "Maintenance",
}

DASHBOARD_TO_STATUS = {
    "Available": RoomUnit.Status.AVAILABLE,
    "Occupied": RoomUnit.Status.OCCUPIED,
    "Reserved": RoomUnit.Status.RESERVED,
    "Cleaning": RoomUnit.Status.CLEANING,
    "Maintenance": RoomUnit.Status.MAINTENANCE,
}


class RoomUnitSerializer(serializers.ModelSerializer):
    room_type_id = serializers.UUIDField(source="room_type.id", read_only=True)
    room_type_name = serializers.CharField(source="room_type.name", read_only=True)
    room_type_slug = serializers.CharField(source="room_type.slug", read_only=True)
    display_name = serializers.CharField(read_only=True)
    number = serializers.CharField(source="code", read_only=True)
    type = serializers.CharField(source="room_type.name", read_only=True)
    rate = serializers.DecimalField(
        source="room_type.base_rate", max_digits=10, decimal_places=2, read_only=True
    )
    beds = serializers.CharField(source="room_type.beds", read_only=True)
    sizeSqFt = serializers.IntegerField(source="room_type.size_sq_ft", read_only=True, allow_null=True)
    amenities = serializers.ListField(source="room_type.amenities", read_only=True)
    imageUrl = serializers.CharField(source="room_type.image", read_only=True)
    dashboardStatus = serializers.SerializerMethodField()
    guest = serializers.SerializerMethodField()
    reservationId = serializers.SerializerMethodField()

    class Meta:
        model = RoomUnit
        fields = (
            "id",
            "code",
            "number",
            "name",
            "display_name",
            "room_type_id",
            "room_type_name",
            "room_type_slug",
            "type",
            "floor",
            "capacity",
            "beds",
            "rate",
            "sizeSqFt",
            "amenities",
            "imageUrl",
            "status",
            "dashboardStatus",
            "housekeeping_status",
            "assignee",
            "notes",
            "guest",
            "reservationId",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_dashboardStatus(self, obj):
        return STATUS_TO_DASHBOARD.get(obj.status, "Available")

    def _current_booking(self, obj):
        from apps.bookings.models import Booking

        blocking = set(Booking.blocking_statuses())
        matches = [booking for booking in obj.bookings.all() if booking.status in blocking]
        if not matches:
            return None
        return max(matches, key=lambda booking: booking.check_in)

    def get_guest(self, obj):
        booking = self._current_booking(obj)
        return booking.guest_name if booking else ""

    def get_reservationId(self, obj):
        booking = self._current_booking(obj)
        return booking.reference if booking else None


class RoomUnitWriteSerializer(serializers.ModelSerializer):
    room_type_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = RoomUnit
        fields = (
            "id",
            "room_type_id",
            "code",
            "name",
            "floor",
            "capacity",
            "status",
            "housekeeping_status",
            "assignee",
            "notes",
            "is_active",
        )
        read_only_fields = ("id",)

    def validate_room_type_id(self, value):
        if not RoomType.objects.filter(id=value).exists():
            raise serializers.ValidationError("Room type not found.")
        return value

    def create(self, validated_data):
        room_type_id = validated_data.pop("room_type_id")
        validated_data["room_type"] = RoomType.objects.get(id=room_type_id)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        room_type_id = validated_data.pop("room_type_id", None)
        if room_type_id:
            instance.room_type = RoomType.objects.get(id=room_type_id)
        return super().update(instance, validated_data)


class RoomUnitStatusSerializer(serializers.ModelSerializer):
    dashboardStatus = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = RoomUnit
        fields = ("status", "housekeeping_status", "assignee", "notes", "dashboardStatus")

    def validate(self, attrs):
        dashboard = attrs.pop("dashboardStatus", None)
        if dashboard:
            mapped = DASHBOARD_TO_STATUS.get(dashboard)
            if not mapped:
                raise serializers.ValidationError({"dashboardStatus": "Unknown room status."})
            attrs["status"] = mapped
            if mapped == RoomUnit.Status.CLEANING:
                attrs.setdefault("housekeeping_status", RoomUnit.HousekeepingStatus.IN_PROGRESS)
            elif mapped == RoomUnit.Status.AVAILABLE:
                attrs.setdefault("housekeeping_status", RoomUnit.HousekeepingStatus.CLEAN)
            elif mapped == RoomUnit.Status.MAINTENANCE:
                attrs.setdefault("housekeeping_status", RoomUnit.HousekeepingStatus.DIRTY)
        return attrs


class StaffRoomTypeSerializer(serializers.ModelSerializer):
    unit_count = serializers.IntegerField(source="active_unit_count", read_only=True)

    class Meta:
        model = RoomType
        fields = (
            "id",
            "name",
            "slug",
            "short_description",
            "description",
            "max_guests",
            "beds",
            "base_rate",
            "size_label",
            "size_sq_ft",
            "amenities",
            "included_services",
            "policies",
            "availability_note",
            "image",
            "gallery",
            "is_active",
            "sort_order",
            "unit_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class StaffRoomTypeWriteSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False, allow_blank=True)

    class Meta:
        model = RoomType
        fields = (
            "id",
            "name",
            "slug",
            "short_description",
            "description",
            "max_guests",
            "beds",
            "base_rate",
            "size_label",
            "size_sq_ft",
            "amenities",
            "included_services",
            "policies",
            "availability_note",
            "image",
            "gallery",
            "is_active",
            "sort_order",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        from django.utils.text import slugify

        name = attrs.get("name") or getattr(self.instance, "name", "")
        slug = (attrs.get("slug") or "").strip() or slugify(name)
        if not slug:
            raise serializers.ValidationError({"name": "Name is required."})
        attrs["slug"] = slug
        return attrs

    def create(self, validated_data):
        slug = validated_data["slug"]
        existing = RoomType.objects.filter(slug=slug).first()
        if existing:
            return super().update(existing, validated_data)
        return super().create(validated_data)
