"""
Main URL configuration for the project.

This file wires the Django admin panel and all version 1 API endpoints
for the project apps.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from apps.orders.views.v1 import (
    CourierAcceptOrderView,
    CourierCancelOrderView,
    CourierDeliverOrderView,
    CourierOrdersView,
    AdminDashboardStatsView,
    AdminOrderListView,
    AdminLocationListView,
    AdminShipmentListView,
    AdminPaymentListView,
    AdminNotificationListView,
)
from apps.tracking.views.mock import mock_track_parcel
from apps.users.views.v1 import (
    LoginView,
    LogoutView,
    RegisterView,
    courier_dashboard_view,
    customer_dashboard_view,
    AdminUserListView,
)

# ============================================================
# SWAGGER / OPENAPI DOCUMENTATION
# ============================================================
schema_view = get_schema_view(
    openapi.Info(
        title="Order Delivery API",
        default_version='v1',
        description="""
        Order Delivery tizimi uchun API dokumentatsiyasi.
        
        **Asosiy funksiyalar:**
        - Foydalanuvchi ro'yxatdan o'tish va autentifikatsiya
        - Manzillarni saqlash va boshqarish
        - Buyurtmalar yaratish va kuzatish
        - Kuryerlar uchun buyurtma qabul qilish
        
        **Autentifikatsiya:**
        JWT token orqali. Avval `/api/login/` dan token oling.
        """,
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # ============================================================
    # API DOCUMENTATION (Swagger UI & ReDoc)
    # ============================================================
    path("api/docs/", schema_view.with_ui('swagger', cache_timeout=0), name="schema-swagger-ui"),
    path("api/redoc/", schema_view.with_ui('redoc', cache_timeout=0), name="schema-redoc"),
    path("api/swagger.json/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    
    # ============================================================
    # Django Admin
    # ============================================================
    path("admin/", admin.site.urls),

    # ============================================================
    # API v1 Endpoints (REST Framework)
    # ============================================================
    path("api/v1/users/", include(("apps.users.urls.v1", "v1"), namespace="users-v1")),
    path("api/v1/orders/", include(("apps.orders.urls.v1", "v1"), namespace="orders-v1")),
    path("api/v1/shipments/", include(("apps.shipments.urls.v1", "v1"), namespace="shipments-v1")),
    path("api/v1/tracking/", include(("apps.tracking.urls.v1", "v1"), namespace="tracking-v1")),
    path("api/v1/locations/", include(("apps.locations.urls.v1", "v1"), namespace="locations-v1")),
    path("api/v1/notifications/", include(("apps.notifications.urls.v1", "v1"), namespace="notifications-v1")),
    path("api/v1/payments/", include(("apps.payments.urls.v1", "v1"), namespace="payments-v1")),
    
    # ============================================================
    # Mock Track API va Auth Endpoints
    # ============================================================
    path("api/track", mock_track_parcel, name="mock_track_parcel"),
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/courier/orders/", CourierOrdersView.as_view(), name="courier-orders"),
    path("api/courier/orders/<int:id>/accept/", CourierAcceptOrderView.as_view(), name="courier-order-accept"),
    path("api/courier/orders/<int:id>/deliver/", CourierDeliverOrderView.as_view(), name="courier-order-deliver"),
    path("api/courier/orders/<int:id>/cancel/", CourierCancelOrderView.as_view(), name="courier-order-cancel"),
    
    # ============================================================
    # Frontend (Web sahifalar)
    # ============================================================
    path("custom-admin/", TemplateView.as_view(template_name="admin_dashboard.html"), name="custom-admin"),
    path("login/", TemplateView.as_view(template_name="login.html"), name="login-page"),
    path("register/", TemplateView.as_view(template_name="register.html"), name="register-page"),
    path("courier-dashboard/", courier_dashboard_view, name="courier_dashboard"),
    path("customer-dashboard/", customer_dashboard_view, name="customer_dashboard"),
    path("app/", TemplateView.as_view(template_name="app.html"), name="app"),
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    
    # Custom Admin API Endpoints
    path("api/v1/admin/dashboard/", AdminDashboardStatsView.as_view(), name="admin-dashboard-stats"),
    path("api/v1/admin/orders/", AdminOrderListView.as_view(), name="admin-orders-list"),
    path("api/v1/admin/users/", AdminUserListView.as_view(), name="admin-users-list"),
    path("api/v1/admin/locations/", AdminLocationListView.as_view(), name="admin-locations-list"),
    path("api/v1/admin/shipments/", AdminShipmentListView.as_view(), name="admin-shipments-list"),
    path("api/v1/admin/payments/", AdminPaymentListView.as_view(), name="admin-payments-list"),
    path("api/v1/admin/notifications/", AdminNotificationListView.as_view(), name="admin-notifications-list"),
    
    # Shared URLs
    path("", include(("apps.shared.urls", "shared"), namespace="shared")),
]