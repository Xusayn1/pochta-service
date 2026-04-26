from rest_framework import serializers

from apps.orders.models import Order
from apps.tracking.serializers.v1 import TrackingEventSerializer
from apps.users.models import PHONE_REGEX, UserAddress


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new orders"""
    order_number = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    estimated_delivery = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    sender_address = serializers.PrimaryKeyRelatedField(
        queryset=UserAddress.objects.none(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Order
        fields = [
            'order_number',
            'sender_address',
            'recipient_name',
            'recipient_phone',
            'recipient_address',
            'item_description',
            'to_region',
            'service_type',
            'weight_kg',
            'declared_value',
            'notes',
            'status',
            'price',
            'estimated_delivery',
            'created_at',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["sender_address"].queryset = UserAddress.objects.filter(user=request.user)

    def validate_recipient_phone(self, value):
        if not PHONE_REGEX.match(value):
            raise serializers.ValidationError("Recipient phone must be in Uzbekistan format: +998XXXXXXXXX.")
        return value

    def validate_weight_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("Weight must be greater than zero.")
        return value

    def validate_declared_value(self, value):
        if value < 0:
            raise serializers.ValidationError("Declared value cannot be negative.")
        return value


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order listing"""
    sender_address_title = serializers.CharField(source='sender_address.title', read_only=True)

    class Meta:
        model = Order
        fields = [
            'order_number',
            'sender_address',
            'sender_address_title',
            'recipient_name',
            'service_type',
            'status',
            'price',
            'estimated_delivery',
            'created_at',
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer with status history"""
    tracking_events = TrackingEventSerializer(many=True, read_only=True)
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    sender_phone = serializers.CharField(source='sender.phone', read_only=True)
    sender_address_title = serializers.CharField(source='sender_address.title', read_only=True)
    sender_address_text = serializers.CharField(source='sender_address.full_address', read_only=True)

    class Meta:
        model = Order
        fields = [
            'order_number',
            'sender',
            'sender_name',
            'sender_phone',
            'sender_address',
            'sender_address_title',
            'sender_address_text',
            'recipient_name',
            'recipient_phone',
            'recipient_address',
            'item_description',
            'to_region',
            'service_type',
            'weight_kg',
            'declared_value',
            'status',
            'notes',
            'price',
            'estimated_delivery',
            'tracking_events',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['order_number', 'sender', 'price', 'created_at', 'updated_at']


class CourierAssignedOrderSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    sender_phone = serializers.CharField(source='sender.phone', read_only=True)

    class Meta:
        model = Order
        fields = [
            'order_number',
            'recipient_name',
            'recipient_phone',
            'recipient_address',
            'sender_name',
            'sender_phone',
            'service_type',
            'status',
            'created_at',
            'updated_at',
        ]


class CourierOrderStatusUpdateSerializer(serializers.Serializer):
    ALLOWED_STATUSES = [
        "picked_up",
        "in_transit",
        "out_for_delivery",
        "delivered",
    ]
    status = serializers.ChoiceField(choices=ALLOWED_STATUSES)
