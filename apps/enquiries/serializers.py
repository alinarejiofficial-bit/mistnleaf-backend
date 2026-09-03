from rest_framework import serializers

from .models import Enquiry


class PublicEnquiryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = ("name", "email", "phone", "subject", "message")

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")
        return value.strip()

    def validate_message(self, value):
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters.")
        return value.strip()

    def create(self, validated_data):
        validated_data["channel"] = Enquiry.Channel.WEBSITE
        return super().create(validated_data)


class StaffEnquirySerializer(serializers.ModelSerializer):
    """Matches mistnleaf_admin Enquiry type (camelCase)."""

    id = serializers.CharField(source="reference", read_only=True)
    receivedAt = serializers.DateTimeField(source="received_at", format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = Enquiry
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "subject",
            "message",
            "channel",
            "status",
            "receivedAt",
            "staff_notes",
        )
        read_only_fields = ("id", "receivedAt", "channel")


class StaffEnquiryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = ("status", "staff_notes", "assigned_to")
