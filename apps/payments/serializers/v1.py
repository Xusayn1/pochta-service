from rest_framework import serializers

from apps.orders.models import Order, PaymentStatus as OrderPaymentStatus
from apps.payments.models import Invoice, Transaction, TransactionStatus


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "order",
            "amount",
            "payment_method",
            "status",
            "transaction_id",
            "payment_url",
            "created_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "transaction_id",
            "payment_url",
            "created_at",
        ]


class TransactionCreateSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(source="order", queryset=Order.objects.all())

    class Meta:
        model = Transaction
        fields = ["order_id", "payment_method"]

    def validate_order_id(self, value):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if value.payment_status == OrderPaymentStatus.PAID:
            raise serializers.ValidationError("This order is already paid.")

        if value.transactions.filter(status=TransactionStatus.COMPLETED).exists():
            raise serializers.ValidationError("This order already has a completed transaction.")

        if user and getattr(user, "is_authenticated", False) and not user.is_staff and value.user_id != user.id:
            raise serializers.ValidationError("You can only create a transaction for your own order.")

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        order = attrs["order"]

        if order.total_price <= 0:
            raise serializers.ValidationError({"order_id": "Order total must be greater than zero."})

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        order = validated_data["order"]

        validated_data["user"] = user if user and getattr(user, "is_authenticated", False) else order.user
        validated_data["amount"] = order.total_price
        validated_data["status"] = TransactionStatus.PENDING

        return super().create(validated_data)


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "amount",
            "tax",
            "discount",
            "total_amount",
            "pdf_file",
            "is_paid",
            "paid_at",
            "created_at",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        amount = attrs.get("amount", getattr(self.instance, "amount", 0))
        tax = attrs.get("tax", getattr(self.instance, "tax", 0))
        discount = attrs.get("discount", getattr(self.instance, "discount", 0))

        if amount < 0:
            raise serializers.ValidationError({"amount": "Amount cannot be negative."})
        if tax < 0:
            raise serializers.ValidationError({"tax": "Tax cannot be negative."})
        if discount < 0:
            raise serializers.ValidationError({"discount": "Discount cannot be negative."})
        if discount > amount + tax:
            raise serializers.ValidationError({"discount": "Discount cannot exceed amount plus tax."})

        return attrs


class PaymentCallbackSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=255)
    status = serializers.ChoiceField(choices=TransactionStatus.choices)
    payment_details = serializers.JSONField()

    def validate_transaction_id(self, value):
        if not Transaction.objects.filter(transaction_id=value).exists():
            raise serializers.ValidationError("Transaction not found.")
        return value

    def validate_payment_details(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Payment details must be a JSON object.")
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        transaction = Transaction.objects.get(transaction_id=attrs["transaction_id"])

        if transaction.status == TransactionStatus.COMPLETED and attrs["status"] != TransactionStatus.REFUNDED:
            raise serializers.ValidationError({"status": "Completed transactions can only move to refunded."})

        attrs["transaction"] = transaction
        return attrs
