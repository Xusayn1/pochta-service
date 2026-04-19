from decimal import Decimal
from datetime import timedelta
import re

from django.utils import timezone
from rest_framework import serializers

from apps.locations.models import District, Region
from apps.orders.models import (
    Order,
    OrderHistory,
    OrderStatus,
    OrderStatusCode,
    PackageType,
    PaymentStatus,
)

try:
    from apps.users.models import User  # noqa: F401
except ImportError:  # pragma: no cover
    User = None  # type: ignore


PHONE_REGEX = re.compile(r"^\+998\d{9}$")
TWOPLACES = Decimal("0.01")


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ["id", "name", "code", "color"]


class PackageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageType
        fields = ["id", "name", "code", "max_weight", "base_price"]


class OrderListSerializer(serializers.ModelSerializer):
    from_region_name = serializers.CharField(source="from_region.name", read_only=True)
    to_region_name = serializers.CharField(source="to_region.name", read_only=True)
    package_type_name = serializers.CharField(source="package_type.name", read_only=True)
    status_name = serializers.CharField(source="status.name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "tracking_number",
            "from_region_name",
            "to_region_name",
            "package_type_name",
            "weight",
            "status_name",
            "total_price",
            "created_at",
            "payment_status",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    package_type = PackageTypeSerializer(read_only=True)
    status = OrderStatusSerializer(read_only=True)
    from_region_name = serializers.CharField(source="from_region.name", read_only=True)
    from_district_name = serializers.CharField(source="from_district.name", read_only=True)
    to_region_name = serializers.CharField(source="to_region.name", read_only=True)
    to_district_name = serializers.CharField(source="to_district.name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "tracking_number",
            "user",
            "from_region",
            "from_region_name",
            "from_district",
            "from_district_name",
            "from_address",
            "from_phone",
            "from_name",
            "to_region",
            "to_region_name",
            "to_district",
            "to_district_name",
            "to_address",
            "to_phone",
            "to_name",
            "package_type",
            "weight",
            "dimensions",
            "description",
            "is_fragile",
            "status",
            "price",
            "delivery_fee",
            "total_price",
            "payment_status",
            "payment_method",
            "estimated_delivery_date",
            "delivered_at",
            "cancelled_at",
            "created_at",
            "updated_at",
            "created_by",
        ]
        read_only_fields = ["tracking_number", "total_price", "created_at", "updated_at"]


class OrderCreateSerializer(serializers.ModelSerializer):
    from_region_id = serializers.PrimaryKeyRelatedField(
        source="from_region",
        queryset=Region.objects.filter(is_active=True),
    )
    from_district_id = serializers.PrimaryKeyRelatedField(
        source="from_district",
        queryset=District.objects.filter(is_active=True).select_related("region"),
    )
    to_region_id = serializers.PrimaryKeyRelatedField(
        source="to_region",
        queryset=Region.objects.filter(is_active=True),
    )
    to_district_id = serializers.PrimaryKeyRelatedField(
        source="to_district",
        queryset=District.objects.filter(is_active=True).select_related("region"),
    )
    package_type_id = serializers.PrimaryKeyRelatedField(
        source="package_type",
        queryset=PackageType.objects.filter(is_active=True),
    )

    class Meta:
        model = Order
        fields = [
            "from_region_id",
            "from_district_id",
            "from_address",
            "from_phone",
            "from_name",
            "to_region_id",
            "to_district_id",
            "to_address",
            "to_phone",
            "to_name",
            "package_type_id",
            "weight",
            "dimensions",
            "description",
            "is_fragile",
            "payment_method",
        ]

    def validate_from_phone(self, value):
        return self._validate_phone(value)

    def validate_to_phone(self, value):
        return self._validate_phone(value)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        from_region = attrs["from_region"]
        from_district = attrs["from_district"]
        to_region = attrs["to_region"]
        to_district = attrs["to_district"]

        if from_district.region_id != from_region.id:
            raise serializers.ValidationError(
                {"from_district_id": "Selected district does not belong to the source region."}
            )
        if to_district.region_id != to_region.id:
            raise serializers.ValidationError(
                {"to_district_id": "Selected district does not belong to the destination region."}
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not user or not getattr(user, "is_authenticated", False):
            raise serializers.ValidationError({"user": "Authenticated user is required to create an order."})

        pending_status, _ = OrderStatus.objects.get_or_create(
            code=OrderStatusCode.PENDING,
            defaults={
                "name": "Pending",
                "color": "#F59E0B",
                "is_active": True,
            },
        )

        price, delivery_fee = self.calculate_delivery_price(validated_data)
        estimated_delivery_date = self.calculate_estimated_delivery_date(validated_data)

        validated_data["user"] = user
        validated_data["created_by"] = user
        validated_data["status"] = pending_status
        validated_data["payment_status"] = PaymentStatus.PENDING
        validated_data["price"] = price
        validated_data["delivery_fee"] = delivery_fee
        validated_data["estimated_delivery_date"] = estimated_delivery_date

        order = super().create(validated_data)
        OrderHistory.objects.create(
            order=order,
            status=pending_status,
            note="Order created",
            created_by=user,
        )
        return order

    def _validate_phone(self, value):
        if not PHONE_REGEX.match(value):
            raise serializers.ValidationError("Phone number must be in Uzbekistan format: +998XXXXXXXXX.")
        return value

    def calculate_delivery_price(self, validated_data):
        package_type = validated_data["package_type"]
        weight = validated_data["weight"]
        is_fragile = validated_data.get("is_fragile", False)
        from_region = validated_data["from_region"]
        from_district = validated_data["from_district"]
        to_region = validated_data["to_region"]
        to_district = validated_data["to_district"]

        if from_district.id == to_district.id:
            distance_fee = Decimal("5000.00")
            delivery_days = 1
        elif from_region.id == to_region.id:
            distance_fee = Decimal("10000.00")
            delivery_days = 2
        else:
            distance_fee = Decimal("20000.00")
            delivery_days = 3

        extra_weight = max(Decimal("0.00"), weight - package_type.max_weight)
        weight_surcharge = extra_weight * Decimal("2500.00")
        fragile_fee = Decimal("7500.00") if is_fragile else Decimal("0.00")

        price = (package_type.base_price + weight_surcharge).quantize(TWOPLACES)
        delivery_fee = (distance_fee + fragile_fee).quantize(TWOPLACES)

        self._delivery_days = delivery_days
        return price, delivery_fee

    def calculate_estimated_delivery_date(self, validated_data):
        delivery_days = getattr(self, "_delivery_days", None)
        if delivery_days is None:
            self.calculate_delivery_price(validated_data)
            delivery_days = getattr(self, "_delivery_days", 3)
        return timezone.localdate() + timedelta(days=delivery_days)


class OrderHistorySerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source="status.name", read_only=True)

    class Meta:
        model = OrderHistory
        fields = ["id", "status_name", "note", "location", "created_at"]
