"""
Main URL configuration for the project.

This file wires the Django admin panel and all version 1 API endpoints
for the project apps.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from apps.orders.views.v1 import (
    CourierAcceptOrderView,
    CourierCancelOrderView,
    CourierDeliverOrderView,
    CourierOrdersView,
)
from apps.tracking.views.mock import mock_track_parcel
from apps.users.views.v1 import LoginView, LogoutView, RegisterView, courier_dashboard_view

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # API v1 endpoints
    path("api/v1/users/", include(("apps.users.urls.v1", "v1"), namespace="users-v1")),
    path("api/v1/orders/", include(("apps.orders.urls.v1", "v1"), namespace="orders-v1")),
    path("api/v1/shipments/", include(("apps.shipments.urls.v1", "v1"), namespace="shipments-v1")),
    path("api/v1/tracking/", include(("apps.tracking.urls.v1", "v1"), namespace="tracking-v1")),
    path("api/v1/locations/", include(("apps.locations.urls.v1", "v1"), namespace="locations-v1")),
    path("api/v1/notifications/", include(("apps.notifications.urls.v1", "v1"), namespace="notifications-v1")),
    path("api/v1/payments/", include(("apps.payments.urls.v1", "v1"), namespace="payments-v1")),
    
    # Mock Track API endpoint
    path("api/track", mock_track_parcel, name="mock_track_parcel"),
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/courier/orders/", CourierOrdersView.as_view(), name="courier-orders"),
    path("api/courier/orders/<int:id>/accept/", CourierAcceptOrderView.as_view(), name="courier-order-accept"),
    path("api/courier/orders/<int:id>/deliver/", CourierDeliverOrderView.as_view(), name="courier-order-deliver"),
    path("api/courier/orders/<int:id>/cancel/", CourierCancelOrderView.as_view(), name="courier-order-cancel"),
    
    # Frontend
    path("login/", TemplateView.as_view(template_name="login.html"), name="login-page"),
    path("register/", TemplateView.as_view(template_name="register.html"), name="register-page"),
    path("courier-dashboard/", courier_dashboard_view, name="courier_dashboard"),
    path("app/", TemplateView.as_view(template_name="app.html"), name="app"),
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    
    path("", include(("apps.shared.urls", "shared"), namespace="shared")),
]
