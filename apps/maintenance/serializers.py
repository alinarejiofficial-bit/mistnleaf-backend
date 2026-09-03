from rest_framework import serializers

from apps.rooms.models import RoomUnit

from .models import MaintenanceTicket


class MaintenanceTicketSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="reference", read_only=True)
    reportedBy = serializers.CharField(source="reported_by")
    reportedAt = serializers.DateTimeField(source="reported_at", format="%Y-%m-%d", read_only=True)
    roomUnitId = serializers.UUIDField(source="room_unit_id", allow_null=True, read_only=True)

    class Meta:
        model = MaintenanceTicket
        fields = (
            "id",
            "room",
            "roomUnitId",
            "issue",
            "category",
            "priority",
            "status",
            "reportedBy",
            "reportedAt",
        )


class MaintenanceTicketWriteSerializer(serializers.ModelSerializer):
    roomUnitId = serializers.UUIDField(required=False, allow_null=True)
    reportedBy = serializers.CharField(source="reported_by", required=False, allow_blank=True)

    class Meta:
        model = MaintenanceTicket
        fields = (
            "room",
            "roomUnitId",
            "issue",
            "category",
            "priority",
            "status",
            "reportedBy",
        )

    def validate_roomUnitId(self, value):
        if value and not RoomUnit.objects.filter(id=value).exists():
            raise serializers.ValidationError("Room not found.")
        return value

    def create(self, validated_data):
        room_unit_id = validated_data.pop("roomUnitId", None)
        if room_unit_id:
            validated_data["room_unit"] = RoomUnit.objects.filter(id=room_unit_id).first()
            unit = validated_data["room_unit"]
            if unit and not validated_data.get("room"):
                validated_data["room"] = unit.display_name
            if unit:
                unit.status = RoomUnit.Status.MAINTENANCE
                unit.save(update_fields=["status", "updated_at"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        room_unit_id = validated_data.pop("roomUnitId", None)
        if room_unit_id:
            instance.room_unit = RoomUnit.objects.filter(id=room_unit_id).first()
        instance = super().update(instance, validated_data)
        if instance.status == MaintenanceTicket.Status.RESOLVED and instance.room_unit:
            if instance.room_unit.status == RoomUnit.Status.MAINTENANCE:
                instance.room_unit.status = RoomUnit.Status.DIRTY
                instance.room_unit.housekeeping_status = RoomUnit.HousekeepingStatus.DIRTY
                instance.room_unit.save(update_fields=["status", "housekeeping_status", "updated_at"])
        return instance
