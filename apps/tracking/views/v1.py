from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from apps.orders.models import Order
from apps.shared.permissions import IsCourier, IsManager
from apps.tracking.models import TrackingEvent
from apps.tracking.serializers.v1 import PublicTrackingSerializer, TrackingEventSerializer


class PublicTrackView(generics.RetrieveAPIView):
    """Public tracking lookup by order number (no auth required)"""
    permission_classes = [permissions.AllowAny]
    serializer_class = PublicTrackingSerializer

    def get(self, request, tracking_number):
        try:
            order = Order.objects.get(order_number=tracking_number)
        except Order.DoesNotExist:
            return Response(
                {"error": "Tracking number not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        events = TrackingEvent.objects.filter(order=order).order_by('-timestamp')

        data = {
            'order_number': order.order_number,
            'status': order.status,
            'recipient_name': order.recipient_name,
            'estimated_delivery': order.estimated_delivery,
            'events': TrackingEventSerializer(events, many=True).data
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)


class AddTrackingEventView(generics.CreateAPIView):
    """Add tracking event to order (courier/admin only)"""
    serializer_class = TrackingEventSerializer
    permission_classes = [IsCourier | IsManager]

    def perform_create(self, serializer):
        order = get_object_or_404(Order, order_number=self.kwargs['tracking_number'])
        tracking_event = serializer.save(order=order, created_by=self.request.user)

        status_map = {
            'order_created': 'confirmed',
            'picked_up': 'picked_up',
            'in_transit': 'in_transit',
            'out_for_delivery': 'out_for_delivery',
            'delivered': 'delivered',
        }
        new_status = status_map.get(tracking_event.event_type)
        if new_status and order.status != new_status:
            Order.objects.filter(pk=order.pk).update(status=new_status, updated_at=timezone.now())
