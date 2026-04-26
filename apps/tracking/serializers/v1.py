from rest_framework import serializers

from apps.shared.utils import mask_name
from apps.tracking.models import TrackingEvent


class TrackingEventSerializer(serializers.ModelSerializer):
    """Serializer for tracking events"""

    class Meta:
        model = TrackingEvent
        fields = [
            'id',
            'event_type',
            'location',
            'description',
            'timestamp',
            'created_by',
        ]
        read_only_fields = ['id', 'timestamp']


class PublicTrackingSerializer(serializers.Serializer):
    """Safe public response for tracking lookup"""

    order_number = serializers.CharField()
    status = serializers.CharField()
    recipient_name = serializers.SerializerMethodField()
    estimated_delivery = serializers.DateTimeField()
    events = TrackingEventSerializer(many=True)

    def get_recipient_name(self, obj):
        return mask_name(obj['recipient_name'])