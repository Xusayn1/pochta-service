"""
Main URL configuration for the project.

This file wires the Django admin panel and all version 1 API endpoints
for the project apps.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # API v1 endpoints
    path("api/v1/locations/", include(("apps.locations.urls.v1", "v1"), namespace="locations-v1")),
    path("api/v1/users/", include(("apps.users.urls.v1", "v1"), namespace="users-v1")),
    path("api/v1/orders/", include(("apps.orders.urls.v1", "v1"), namespace="orders-v1")),
    path("api/v1/payments/", include(("apps.payments.urls.v1", "v1"), namespace="payments-v1")),
]
