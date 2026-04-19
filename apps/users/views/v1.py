import random

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import permissions, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import UserAddress
from apps.users.serializers.v1 import (
    OTPSendSerializer,
    UserAddressSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

OTP_CACHE_PREFIX = "users:otp:"
OTP_TTL_SECONDS = 300


def generate_otp_code():
    return f"{random.randint(0, 999999):06d}"


def cache_otp(phone):
    otp_code = generate_otp_code()
    cache.set(f"{OTP_CACHE_PREFIX}{phone}", otp_code, OTP_TTL_SECONDS)
    return otp_code


def verify_otp(phone, otp):
    cached_otp = cache.get(f"{OTP_CACHE_PREFIX}{phone}")
    return cached_otp and cached_otp == otp


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user_id == request.user.id


class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPSendSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        cache_otp(phone)

        return Response(
            {"detail": "OTP sent successfully."},
            status=status.HTTP_200_OK,
        )


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        phone = getattr(user, "phone", serializer.validated_data.get("phone"))
        if phone:
            cache_otp(phone)

        return Response(
            {
                "detail": "Registration successful. OTP sent.",
                "user_id": user.pk,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        otp = serializer.validated_data["otp"]

        if not verify_otp(phone, otp):
            return Response(
                {"detail": "Invalid or expired OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_model = get_user_model()
        user = user_model.objects.filter(phone=phone).first()
        if user is None:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cache.delete(f"{OTP_CACHE_PREFIX}{phone}")
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=partial,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserAddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = UserAddress.objects.select_related("region", "district", "user").all()
    serializer_class = UserAddressSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def perform_create(self, serializer):
        is_default = serializer.validated_data.get("is_default", False)

        if is_default:
            UserAddress.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
        elif not UserAddress.objects.filter(user=self.request.user).exists():
            serializer.validated_data["is_default"] = True

        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        is_default = serializer.validated_data.get("is_default", serializer.instance.is_default)

        if is_default:
            UserAddress.objects.filter(user=self.request.user, is_default=True).exclude(
                pk=serializer.instance.pk
            ).update(is_default=False)

        serializer.save()

    def perform_destroy(self, instance):
        address_model = type(instance)
        was_default = getattr(instance, "is_default", False)
        user = instance.user

        instance.delete()

        if was_default:
            next_address = address_model.objects.filter(user=user).order_by("-id").first()
            if next_address:
                next_address.is_default = True
                next_address.save(update_fields=["is_default"])


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )
