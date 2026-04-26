from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.serializers.v1 import PaymentCreateSerializer, PaymentSerializer


class PaymentCreateView(generics.CreateAPIView):
    """Create a payment for an order"""
    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.validated_data['order']
        # Check if user owns the order or is manager
        if not (self.request.user.is_manager or order.sender == self.request.user):
            raise permissions.PermissionDenied("You can only create payments for your own orders")
        serializer.save()


class PaymentStatusView(generics.RetrieveAPIView):
    """Get payment status by order number"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        order_number = self.kwargs['order_number']
        order = get_object_or_404(Order, order_number=order_number)

        # Check if user owns the order or is manager
        if not (self.request.user.is_manager or order.sender == self.request.user):
            raise permissions.PermissionDenied("You can only view payments for your own orders")

        return get_object_or_404(Payment, order=order)