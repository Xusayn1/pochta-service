import os
from typing import Any, cast
from uuid import uuid4

from django.http import FileResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from apps.orders.models import PaymentStatus as OrderPaymentStatus
from apps.payments.models import (
    Invoice,
    PaymentMethod,
    PaymentGatewaySettings,
    Transaction,
    TransactionStatus,
)
from apps.payments.serializers.v1 import (
    InvoiceSerializer,
    PaymentCallbackSerializer,
    TransactionCreateSerializer,
    TransactionSerializer,
)


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user_id == request.user.id


class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    queryset = Transaction.objects.select_related("order", "user").all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):  # type: ignore
        if self.action == "create":
            return TransactionCreateSerializer
        return TransactionSerializer

    def get_permissions(self):
        if self.action in ["list", "create", "retrieve", "status"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        transaction = serializer.save()
        if not transaction.transaction_id:
            transaction.transaction_id = f"TXN-{uuid4().hex.upper()}"
        if not transaction.payment_url and transaction.payment_method != PaymentMethod.CASH:
            transaction.payment_url = (
                f"https://payments.example.com/{transaction.payment_method}/{transaction.transaction_id}"
            )
        transaction.save(update_fields=["transaction_id", "payment_url", "updated_at"])

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        transaction = self.get_object()
        serializer = self.get_serializer(transaction)
        return Response(serializer.data)


class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, gateway_name=None):
        serializer = PaymentCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        gateway = self._get_gateway(gateway_name)
        if gateway is None:
            return Response({"detail": "Payment gateway is not configured."}, status=status.HTTP_404_NOT_FOUND)

        if not self._is_signature_valid(request, gateway):
            return Response({"detail": "Invalid signature."}, status=status.HTTP_403_FORBIDDEN)

        transaction = cast(Transaction, validated_data["transaction"])
        callback_status = cast(str, validated_data["status"])
        payment_details = cast(dict[str, Any], validated_data["payment_details"])

        transaction.status = callback_status
        transaction.metadata = payment_details
        transaction.save()

        order = transaction.order
        if callback_status == TransactionStatus.COMPLETED:
            order.payment_status = OrderPaymentStatus.PAID
            invoice = getattr(order, "invoice", None)
            if invoice is not None:
                invoice.is_paid = True
                invoice.save(update_fields=["is_paid", "paid_at"])
        elif callback_status == TransactionStatus.REFUNDED:
            order.payment_status = OrderPaymentStatus.REFUNDED
            invoice = getattr(order, "invoice", None)
            if invoice is not None:
                invoice.is_paid = False
                invoice.save(update_fields=["is_paid", "paid_at"])
        else:
            order.payment_status = OrderPaymentStatus.PENDING
        order.save(update_fields=["payment_status", "updated_at"])

        return Response({"detail": "Webhook processed successfully."}, status=status.HTTP_200_OK)

    def _get_gateway(self, gateway_name):
        if not gateway_name:
            return None
        return PaymentGatewaySettings.objects.filter(gateway_name=gateway_name, is_active=True).first()

    def _is_signature_valid(self, request, gateway):
        signature = request.headers.get("X-Signature") or request.data.get("signature")
        return bool(signature and gateway.secret_key and signature == gateway.secret_key)


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.select_related("order").all()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(order__user=self.request.user)

    def get_permissions(self):
        if self.action in ["list", "retrieve", "download"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        invoice = self.get_object()
        if not invoice.pdf_file:
            return Response({"detail": "Invoice PDF not found."}, status=status.HTTP_404_NOT_FOUND)

        invoice.pdf_file.open("rb")
        filename = os.path.basename(invoice.pdf_file.name)
        return FileResponse(invoice.pdf_file, as_attachment=True, filename=filename)
