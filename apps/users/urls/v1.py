from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.views.v1 import (
    LoginView,
    LogoutView,
    RegisterView,
    SendOTPView,
    UserAddressViewSet,
    UserProfileView,
)


app_name = "v1"

router = DefaultRouter()
router.register("addresses", UserAddressViewSet, basename="addresses")

urlpatterns = [path("", include(router.urls))] + [
    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
