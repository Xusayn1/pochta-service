from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.views.v1 import (
    AddressDetailView,
    AddressListCreateView,
    LoginView,
    LogoutView,
    ProfileView,
    RegisterView,
    courier_dashboard_view,
    customer_dashboard_view,
)

app_name = "v1"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("addresses/", AddressListCreateView.as_view(), name="address-list-create"),
    path("addresses/<int:pk>/", AddressDetailView.as_view(), name="address-detail"),
    path("courier-dashboard/", courier_dashboard_view, name="courier-dashboard"),
    path("customer-dashboard/", customer_dashboard_view, name="customer-dashboard"),
]
