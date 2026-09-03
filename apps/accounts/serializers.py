from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .permissions import (
    LOCKED_ROLE_ID,
    ROLE_DESCRIPTIONS,
    ROLE_LABELS,
    ROLE_PERMISSIONS,
    SYSTEM_LEVEL_PERMISSIONS,
    base_permissions_for_role,
)
from .rbac import apply_super_admin_flags, effective_permissions

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="full_name", read_only=True)
    role_id = serializers.CharField(source="role", read_only=True)
    role_name = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "name",
            "phone",
            "role_id",
            "role_name",
            "department",
            "permissions",
            "is_active",
            "is_staff",
            "last_login",
            "created_at",
        )
        read_only_fields = fields

    def get_role_name(self, obj: User) -> str:
        return ROLE_LABELS.get(obj.role, obj.get_role_display())

    def get_permissions(self, obj: User) -> list[str]:
        if obj.is_superuser or obj.role == LOCKED_ROLE_ID:
            return effective_permissions(LOCKED_ROLE_ID)
        return effective_permissions(obj.role)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone")
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "phone": {"required": False},
        }


class StaffUserWriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    role_id = serializers.CharField(source="role", required=False)
    status = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "name",
            "first_name",
            "last_name",
            "phone",
            "role_id",
            "department",
            "password",
            "status",
            "is_active",
        )
        extra_kwargs = {
            "username": {"required": False},
            "email": {"required": False},
        }

    def validate_role_id(self, value):
        valid = {choice[0] for choice in User.Role.choices}
        if value not in valid:
            raise serializers.ValidationError("Invalid role.")
        return value

    def _apply_name(self, validated):
        name = validated.pop("name", None)
        if not name:
            return
        parts = name.strip().split(" ", 1)
        validated["first_name"] = parts[0]
        validated["last_name"] = parts[1] if len(parts) > 1 else ""

    def _apply_status(self, validated):
        status = validated.pop("status", None)
        if status == "Disabled":
            validated["is_active"] = False
        elif status in ("Active", "Invited"):
            validated["is_active"] = True

    def create(self, validated_data):
        self._apply_name(validated_data)
        self._apply_status(validated_data)
        password = validated_data.pop("password", None) or User.objects.make_random_password()
        email = validated_data["email"].strip().lower()
        validated_data["email"] = email
        validated_data.setdefault("username", email.split("@")[0])
        user = User(**validated_data)
        apply_super_admin_flags(user, user.role)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        self._apply_name(validated_data)
        self._apply_status(validated_data)
        password = validated_data.pop("password", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        apply_super_admin_flags(instance, instance.role)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class StaffRoleSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    locked = serializers.BooleanField()
    permissions = serializers.ListField(child=serializers.CharField())
    base_permissions = serializers.ListField(child=serializers.CharField())
    system_level_permissions = serializers.ListField(child=serializers.CharField())


class StaffRoleWriteSerializer(serializers.Serializer):
    permissions = serializers.ListField(child=serializers.CharField(), allow_empty=True)


class PropertySettingsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120, required=False)
    timezone = serializers.CharField(max_length=64, required=False)
    currency = serializers.CharField(max_length=8, required=False)
    checkInTime = serializers.CharField(max_length=8, required=False)
    checkOutTime = serializers.CharField(max_length=8, required=False)
    taxPercent = serializers.CharField(max_length=8, required=False)


def serialize_role(role_id: str) -> dict:
    return {
        "id": role_id,
        "name": ROLE_LABELS[role_id],
        "description": ROLE_DESCRIPTIONS[role_id],
        "locked": role_id == LOCKED_ROLE_ID,
        "permissions": effective_permissions(role_id),
        "base_permissions": base_permissions_for_role(role_id),
        "system_level_permissions": sorted(SYSTEM_LEVEL_PERMISSIONS),
    }


def all_role_payloads() -> list[dict]:
    return [serialize_role(role_id) for role_id in ROLE_PERMISSIONS]


class LoginSerializer(TokenObtainPairSerializer):
    """JWT login using email + password."""

    username_field = User.EMAIL_FIELD

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
