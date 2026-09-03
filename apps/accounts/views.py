from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.drf_permissions import HasPermission
from apps.accounts.models import PropertySettings
from apps.accounts.rbac import (
    assert_can_assign_role,
    assert_can_manage_target,
    assert_not_last_super_admin,
    is_super_administrator,
    save_role_permissions,
    user_has_effective_permission,
)

User = get_user_model()

from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    PropertySettingsSerializer,
    StaffRoleWriteSerializer,
    StaffUserWriteSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
    all_role_payloads,
    serialize_role,
)


class LoginView(TokenObtainPairView):
    """Authenticate with email and password; returns JWT access + refresh tokens."""

    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Login",
        description="Obtain JWT access and refresh tokens using staff email and password.",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RefreshTokenView(TokenRefreshView):
    """Exchange a valid refresh token for a new access token."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Refresh token",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """Blacklist the refresh token to log out."""

    @extend_schema(
        summary="Logout",
        description="Blacklist the provided refresh token.",
        request=LogoutSerializer,
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = RefreshToken(serializer.validated_data["refresh"])
        token.blacklist()
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class MeView(generics.RetrieveUpdateAPIView):
    """Return or update the authenticated user's profile."""

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return UserProfileUpdateSerializer
        return UserSerializer

    @extend_schema(summary="Current user", tags=["Authentication"])
    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(summary="Update profile", tags=["Authentication"])
    def patch(self, request, *args, **kwargs):
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class StaffUserViewSet(viewsets.ModelViewSet):
    """Staff directory — list, create, update, and delete users."""

    permission_classes = [permissions.IsAuthenticated, HasPermission]
    pagination_class = None
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    queryset = User.objects.all().order_by("first_name", "email")

    @property
    def permission_required(self):
        if self.action in ("list", "retrieve"):
            return ["manage_users", "manage_staff", "manage_housekeeping"]
        if self.action == "destroy":
            return "manage_users"
        return ["manage_users", "manage_staff"]

    def get_queryset(self):
        qs = User.objects.all().order_by("first_name", "email")
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)
        return qs

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return StaffUserWriteSerializer
        return UserSerializer

    @extend_schema(summary="List staff users", tags=["Staff — Users"])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Create staff user", tags=["Staff — Users"])
    def create(self, request, *args, **kwargs):
        serializer = StaffUserWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role_id = serializer.validated_data.get("role") or User.Role.FRONT_DESK
        assert_can_assign_role(request.user, role_id)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Update staff user", tags=["Staff — Users"])
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        assert_can_manage_target(request.user, instance)
        serializer = StaffUserWriteSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        next_role = serializer.validated_data.get("role", instance.role)
        if "role" in serializer.validated_data:
            assert_can_assign_role(request.user, next_role)
        next_active = serializer.validated_data.get("is_active", instance.is_active)
        assert_not_last_super_admin(instance, next_role=next_role, next_active=next_active)
        serializer.save()
        return Response(UserSerializer(instance).data)

    @extend_schema(summary="Delete staff user", tags=["Staff — Users"])
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        assert_can_manage_target(request.user, instance, deleting=True)
        assert_not_last_super_admin(instance, next_role="front_desk", next_active=False)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StaffRoleListView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    permission_required = ["manage_roles", "manage_users", "manage_staff"]

    @extend_schema(summary="List roles and permissions", tags=["Staff — Roles"])
    def get(self, request):
        return Response(all_role_payloads())


class StaffRoleDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasPermission]

    @property
    def permission_required(self):
        if self.request.method == "GET":
            return ["manage_roles", "manage_users", "manage_staff"]
        return "manage_roles"

    @extend_schema(summary="Get role", tags=["Staff — Roles"])
    def get(self, request, role_id):
        from apps.accounts.permissions import ROLE_PERMISSIONS

        if role_id not in ROLE_PERMISSIONS:
            return Response({"detail": "Unknown role."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_role(role_id))

    @extend_schema(summary="Update role permissions", tags=["Staff — Roles"])
    def patch(self, request, role_id):
        serializer = StaffRoleWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        save_role_permissions(role_id, serializer.validated_data["permissions"], request.user)
        return Response(serialize_role(role_id))


class StaffSettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasPermission]

    @property
    def permission_required(self):
        if self.request.method == "GET":
            return ["manage_settings", "view_limited_settings"]
        return ["manage_settings", "view_limited_settings"]

    def _payload(self, settings_obj):
        return {
            "name": settings_obj.name,
            "timezone": settings_obj.timezone,
            "currency": settings_obj.currency,
            "checkInTime": settings_obj.check_in_time,
            "checkOutTime": settings_obj.check_out_time,
            "taxPercent": settings_obj.tax_percent,
        }

    @extend_schema(summary="Property settings", tags=["Staff — Settings"])
    def get(self, request):
        return Response(self._payload(PropertySettings.load()))

    @extend_schema(summary="Update property settings", tags=["Staff — Settings"])
    def put(self, request):
        serializer = PropertySettingsSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        obj = PropertySettings.load()
        full = is_super_administrator(request.user) or user_has_effective_permission(
            request.user, "manage_settings"
        )
        if full:
            obj.name = data.get("name", obj.name)
            obj.timezone = data.get("timezone", obj.timezone)
            obj.currency = data.get("currency", obj.currency)
            obj.tax_percent = data.get("taxPercent", obj.tax_percent)
        obj.check_in_time = data.get("checkInTime", obj.check_in_time)
        obj.check_out_time = data.get("checkOutTime", obj.check_out_time)
        obj.save()
        return Response(self._payload(obj))
