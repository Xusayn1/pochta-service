from rest_framework import serializers

from apps.payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Full payment details serializer"""

    class Meta:
        model = Payment
        fields = [
            'id',
            'order',
            'amount',
            'method',
            'status',
            'transaction_id',
            'paid_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'paid_at', 'created_at', 'updated_at']


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments"""

    class Meta:
        model = Payment
        fields = ['order', 'amount', 'method']
        extra_kwargs = {
            'amount': {'required': False},
        }

    def validate(self, attrs):
        order = attrs['order']
        if hasattr(order, 'payment'):
            raise serializers.ValidationError({"order": "A payment already exists for this order."})

        if attrs.get('amount') is not None and attrs['amount'] <= 0:
            raise serializers.ValidationError({"amount": "Amount must be greater than zero."})
        return attrs

    def create(self, validated_data):
        if not validated_data.get('amount'):
            validated_data['amount'] = validated_data['order'].price
        return super().create(validated_data)
