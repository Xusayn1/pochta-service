from rest_framework import serializers

from apps.shipments.models import Shipment


class ShipmentSerializer(serializers.ModelSerializer):
    """Full shipment details serializer"""

    class Meta:
        model = Shipment
        fields = [
            'id',
            'order',
            'courier',
            'pickup_address',
            'delivery_address',
            'pickup_time',
            'delivery_time',
            'distance_km',
            'shipment_status',
            'weight',
            'dimensions',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShipmentAssignCourierSerializer(serializers.ModelSerializer):
    """Serializer for assigning courier to shipment"""

    class Meta:
        model = Shipment
        fields = ['courier']