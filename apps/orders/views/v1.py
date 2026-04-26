from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.orders.models import Order
from apps.shipments.models import Shipment
from apps.orders.serializers.v1 import (
    CourierAssignedOrderSerializer,
    CourierOrderStatusUpdateSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
)
from apps.shared.permissions import IsCourier, IsManager, IsOwnerOrAdmin
from apps.tracking.models import TrackingEvent


class OrderCreateView(generics.CreateAPIView):
    """Create a new order"""
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class OrderListView(generics.ListAPIView):
    """List orders for authenticated user"""
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(sender=self.request.user).select_related('to_region', 'sender_address')


class OrderDetailView(generics.RetrieveAPIView):
    """Get order details by order number"""
    serializer_class = OrderDetailSerializer
    permission_classes = [IsOwnerOrAdmin]
    lookup_field = 'order_number'
    lookup_url_kwarg = 'order_number'

    def get_queryset(self):
        return Order.objects.select_related('sender', 'to_region', 'sender_address').prefetch_related('tracking_events')


class CourierAssignedOrdersView(generics.ListAPIView):
    serializer_class = CourierAssignedOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourier]

    def get_queryset(self):
        return (
            Order.objects.filter(shipment__courier=self.request.user)
            .select_related('sender')
            .order_by('-updated_at')
        )


class CourierOrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCourier | IsManager]

    event_type_map = {
        "picked_up": "picked_up",
        "in_transit": "in_transit",
        "out_for_delivery": "out_for_delivery",
        "delivered": "delivered",
    }

    def patch(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)
        shipment = getattr(order, "shipment", None)

        if not request.user.is_manager:
            if shipment is None or shipment.courier_id != request.user.id:
                return Response({"detail": "Order is not assigned to this courier."}, status=403)

        serializer = CourierOrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]
        if order.status != new_status:
            order.status = new_status
            order.save(update_fields=["status", "updated_at"])
            TrackingEvent.objects.create(
                order=order,
                event_type=self.event_type_map[new_status],
                location=order.to_region.name_en if order.to_region else "Dispatch center",
                description=f"Order status updated to {new_status.replace('_', ' ')}.",
                created_by=request.user,
                timestamp=timezone.now(),
            )

        return Response(OrderDetailSerializer(order).data)


class CourierOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCourier]

    def _serialize_order(self, order, assigned_to_me=False):
        customer_name = order.sender.full_name or order.sender.username or order.sender.phone
        return {
            "id": order.id,
            "order_number": order.order_number,
            "customer_name": customer_name,
            "address": order.recipient_address,
            "phone": order.recipient_phone,
            "status": order.status,
            "service_type": order.service_type,
            "assigned_to_me": assigned_to_me,
        }

    def get(self, request):
        assigned_orders = (
            Order.objects.filter(shipment__courier=request.user)
            .select_related("sender", "shipment")
            .order_by("-updated_at")
        )
        available_orders = (
            Order.objects.filter(status__in=["pending", "confirmed"])
            .filter(Q(shipment__isnull=True) | Q(shipment__courier__isnull=True))
            .select_related("sender")
            .order_by("-created_at")
        )

        assigned_payload = []
        history_payload = []
        for order in assigned_orders:
            payload = self._serialize_order(order, assigned_to_me=True)
            if order.status in ["delivered", "cancelled"]:
                history_payload.append(payload)
            else:
                assigned_payload.append(payload)

        available_payload = [self._serialize_order(order) for order in available_orders]

        return Response({
            "available_orders": available_payload,
            "assigned_orders": assigned_payload,
            "history_orders": history_payload,
        })


class CourierAcceptOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCourier]

    def post(self, request, id):
        order = get_object_or_404(Order.objects.select_related("shipment", "sender_address"), id=id)
        shipment = getattr(order, "shipment", None)

        if order.status in ["delivered", "cancelled"]:
            return Response({"detail": "This order cannot be accepted."}, status=400)

        if shipment and shipment.courier_id and shipment.courier_id != request.user.id:
            return Response({"detail": "Order is already assigned to another courier."}, status=409)

        if shipment is None:
            shipment = Shipment.objects.create(
                order=order,
                courier=request.user,
                pickup_address=getattr(order.sender_address, "full_address", "") or "Pickup address not provided",
                delivery_address=order.recipient_address,
                weight=order.weight_kg,
                shipment_status=order.status,
            )
        else:
            shipment.courier = request.user
            shipment.pickup_address = shipment.pickup_address or getattr(order.sender_address, "full_address", "")
            shipment.delivery_address = shipment.delivery_address or order.recipient_address
            shipment.weight = shipment.weight or order.weight_kg
            shipment.save(update_fields=["courier", "pickup_address", "delivery_address", "weight", "updated_at"])

        if order.status in ["pending", "confirmed"]:
            order.status = "out_for_delivery"
            order.save(update_fields=["status", "updated_at"])
            TrackingEvent.objects.create(
                order=order,
                event_type="out_for_delivery",
                location=order.to_region.name_en if order.to_region else "Dispatch center",
                description="Courier accepted the order and started delivery.",
                created_by=request.user,
                timestamp=timezone.now(),
            )

        return Response({"detail": "Order accepted successfully.", "order_id": order.id, "status": order.status})


class CourierDeliverOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCourier]

    def post(self, request, id):
        order = get_object_or_404(Order.objects.select_related("shipment"), id=id)
        shipment = getattr(order, "shipment", None)

        if shipment is None or shipment.courier_id != request.user.id:
            return Response({"detail": "Order is not assigned to this courier."}, status=403)

        if order.status == "delivered":
            return Response({"detail": "Order is already delivered."}, status=400)

        order.status = "delivered"
        order.save(update_fields=["status", "updated_at"])

        shipment.delivery_time = timezone.now()
        shipment.shipment_status = "delivered"
        shipment.save(update_fields=["delivery_time", "shipment_status", "updated_at"])

        TrackingEvent.objects.create(
            order=order,
            event_type="delivered",
            location=order.to_region.name_en if order.to_region else "Destination",
            description="Order marked as delivered by courier.",
            created_by=request.user,
            timestamp=timezone.now(),
        )

        return Response({"detail": "Order marked as delivered.", "order_id": order.id, "status": order.status})


class CourierCancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCourier]

    def post(self, request, id):
        order = get_object_or_404(Order.objects.select_related("shipment"), id=id)
        shipment = getattr(order, "shipment", None)

        if shipment is None or shipment.courier_id != request.user.id:
            return Response({"detail": "Order is not assigned to this courier."}, status=403)

        if order.status in ["delivered", "cancelled"]:
            return Response({"detail": "Order cannot be cancelled now."}, status=400)

        order.status = "cancelled"
        order.save(update_fields=["status", "updated_at"])
        shipment.shipment_status = "cancelled"
        shipment.save(update_fields=["shipment_status", "updated_at"])

        return Response({"detail": "Order cancelled.", "order_id": order.id, "status": order.status})
