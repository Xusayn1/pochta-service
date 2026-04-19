from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.payments.views.v1 import InvoiceViewSet, PaymentWebhookView, TransactionViewSet


app_name = "v1"

router = DefaultRouter()
router.register("transactions", TransactionViewSet, basename="transactions")
router.register("invoices", InvoiceViewSet, basename="invoices")

urlpatterns = [
    path("", include(router.urls)),
    path("webhook/click/", PaymentWebhookView.as_view(), {"gateway_name": "click"}, name="click-webhook"),
    path("webhook/payme/", PaymentWebhookView.as_view(), {"gateway_name": "payme"}, name="payme-webhook"),
]
