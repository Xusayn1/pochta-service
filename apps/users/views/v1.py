"""
User authentication, profile, and dashboard views.

This module handles:
- User registration and login (REST API)
- Dashboard templates for browser clients
- User profile management
- Address management
"""

import logging
from typing import cast

from django.shortcuts import redirect, render
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User, UserAddress
from apps.users.serializers.v1 import (
    UserAddressSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegisterSerializer,
)

logger = logging.getLogger(__name__)


def get_tokens_for_user(user: User) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def get_redirect_url(user: User) -> str:
    if user.is_courier:
        return "/courier-dashboard/"

    if user.is_manager:
        return "/custom-admin/"

    return "/customer-dashboard/"


def build_auth_response(user: User) -> dict:
    tokens = get_tokens_for_user(user)
    return {
        "user": UserProfileSerializer(user).data,
        "tokens": tokens,
        "refresh": tokens["refresh"],
        "access": tokens["access"],
        "redirect_to": get_redirect_url(user),
    }


def should_redirect_to_dashboard(request) -> bool:
    """Return True when a browser form expects a redirect instead of JSON."""
    accept_header = request.META.get("HTTP_ACCEPT", "")
    content_type = request.META.get("CONTENT_TYPE", "")
    return "text/html" in accept_header and "application/json" not in content_type


def courier_dashboard_view(request):
    """Render the courier dashboard shell."""
    return render(request, "courier_dashboard.html")


def customer_dashboard_view(request):
    """Render the customer dashboard shell."""
    return render(request, "customer_dashboard.html")


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = cast(User, serializer.save())
            return Response(
                build_auth_response(user),
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Authenticate a user and return JWT tokens."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = cast(User, serializer.validated_data["user"])  # type: ignore[index]
        redirect_to = get_redirect_url(user)

        if should_redirect_to_dashboard(request):
            return redirect(redirect_to)

        return Response(build_auth_response(user), status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Logout user and blacklist refresh token when provided."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                return Response(
                    {"detail": "Invalid refresh token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"detail": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    """Get or update authenticated user profile."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AddressListCreateView(generics.ListCreateAPIView):
    """List and create addresses for the authenticated user."""

    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  # type: ignore[override]
        return UserAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as exc:
            logger.error(
                "Error creating address for user %s: %s",
                self.request.user.id,
                exc,
                exc_info=True,
            )
            raise

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as exc:
            logger.error("Address creation error: %s", exc, exc_info=True)
            return Response(
                {"error": "Failed to create address", "details": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a user-owned address."""

    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  # type: ignore[override]
        return UserAddress.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        user = instance.user
        was_default = instance.is_default
        instance.delete()

        if was_default:
            next_address = (
                UserAddress.objects.filter(user=user)
                .order_by("-created_at")
                .first()
            )
            if next_address:
                next_address.is_default = True
                next_address.save(update_fields=["is_default"])


class AdminUserListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        users = User.objects.all().order_by("-created_at")[:100]
        results = []
        for user in users:
            results.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "phone": user.phone,
                    "email": user.email,
                    "role": user.role,
                    "created_at": user.created_at,
                }
            )
        return Response({"results": results})
