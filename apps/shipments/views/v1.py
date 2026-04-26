from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.shared.permissions import IsManager
from apps.shipments.models import Shipment
from apps.shipments.serializers.v1 import ShipmentAssignCourierSerializer, ShipmentSerializer


class ShipmentDetailView(generics.RetrieveAPIView):
    """Get shipment details by ID"""
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Shipment.objects.all()


class AssignCourierView(generics.UpdateAPIView):
    """Assign courier to shipment (admin only)"""
    serializer_class = ShipmentAssignCourierSerializer
    permission_classes = [IsManager]
    queryset = Shipment.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)