from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import UserAddress
from apps.users.serializers.v1 import (
    UserAddressSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegisterSerializer,
)

User = get_user_model()


def build_auth_response(user):
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    refresh_token = str(refresh)
    redirect_to = "/courier-dashboard/" if getattr(user, "is_courier", False) else "/"
    return {
        'user': UserProfileSerializer(user).data,
        'tokens': {
            'refresh': refresh_token,
            'access': access,
        },
        'refresh': refresh_token,
        'access': access,
        'redirect_to': redirect_to,
    }


def should_redirect_to_dashboard(request):
    accept_header = request.META.get("HTTP_ACCEPT", "")
    content_type = request.META.get("CONTENT_TYPE", "")
    return "text/html" in accept_header and "application/json" not in content_type


@login_required
def courier_dashboard_view(request):
    if not request.user.is_courier:
        return redirect("home")
    return render(request, "courier_dashboard.html")


class RegisterView(APIView):
    """Register a new user account"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user.is_courier and should_redirect_to_dashboard(request):
                return redirect("courier_dashboard")
            return Response(build_auth_response(user), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Authenticate user and return JWT tokens"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            if user.is_courier and should_redirect_to_dashboard(request):
                return redirect("courier_dashboard")
            return Response(build_auth_response(user))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    """Get or update user profile"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressListCreateView(generics.ListCreateAPIView):
    """List and create addresses for the authenticated user"""
    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user).select_related("region", "city")


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a user-owned address"""
    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user).select_related("region", "city")

    def perform_destroy(self, instance):
        user = instance.user
        was_default = instance.is_default
        instance.delete()

        if was_default:
            next_address = UserAddress.objects.filter(user=user).order_by("-created_at").first()
            if next_address:
                next_address.is_default = True
                next_address.save(update_fields=["is_default"])
