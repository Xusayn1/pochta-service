from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string


class OrderStatusCode(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    PICKED_UP = "picked_up", "Picked Up"
    IN_TRANSIT = "in_transit", "In Transit"
    AT_CITY = "at_city", "At City"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"
    RETURNED = "returned", "Returned"


class PackageTypeCode(models.TextChoices):
    DOCUMENT = "document", "Document"
    SMALL = "small", "Small"
    MEDIUM = "medium", "Medium"
    LARGE = "large", "Large"
    FRAGILE = "fragile", "Fragile"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    REFUNDED = "refunded", "Refunded"


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Cash"
    CARD = "card", "Card"
    CLICK = "click", "Click"
    PAYME = "payme", "Payme"


class OrderStatus(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, choices=OrderStatusCode.choices, unique=True)
    color = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "orders_order_status"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PackageType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, choices=PackageTypeCode.choices, unique=True)
    max_weight = models.DecimalField(max_digits=8, decimal_places=2)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "orders_package_type"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Order(models.Model):
    tracking_number = models.CharField(max_length=32, unique=True, db_index=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    from_region = models.ForeignKey(
        "locations.Region",
        on_delete=models.PROTECT,
        related_name="sent_orders",
    )
    from_district = models.ForeignKey(
        "locations.District",
        on_delete=models.PROTECT,
        related_name="sent_orders",
    )
    from_address = models.TextField()
    from_phone = models.CharField(max_length=20)
    from_name = models.CharField(max_length=255)

    to_region = models.ForeignKey(
        "locations.Region",
        on_delete=models.PROTECT,
        related_name="received_orders",
    )
    to_district = models.ForeignKey(
        "locations.District",
        on_delete=models.PROTECT,
        related_name="received_orders",
    )
    to_address = models.TextField()
    to_phone = models.CharField(max_length=20)
    to_name = models.CharField(max_length=255)

    package_type = models.ForeignKey("PackageType", on_delete=models.PROTECT, related_name="orders")
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    dimensions = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_fragile = models.BooleanField(default=False)

    status = models.ForeignKey("OrderStatus", on_delete=models.PROTECT, related_name="orders")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    delivery_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), editable=False)

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)

    estimated_delivery_date = models.DateField()
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_orders",
    )

    class Meta:
        db_table = "orders_order"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tracking_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return self.tracking_number

    @staticmethod
    def generate_tracking_number():
        date_part = timezone.now().strftime("%Y%m%d")
        random_part = get_random_string(6, allowed_chars="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return f"ORD{date_part}{random_part}"

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            tracking_number = self.generate_tracking_number()
            while Order.objects.filter(tracking_number=tracking_number).exists():
                tracking_number = self.generate_tracking_number()
            self.tracking_number = tracking_number

        self.total_price = (self.price or Decimal("0.00")) + (self.delivery_fee or Decimal("0.00"))

        if self.status_id and self.status.code == OrderStatusCode.DELIVERED and not self.delivered_at:
            self.delivered_at = timezone.now()
        if self.status_id and self.status.code == OrderStatusCode.CANCELLED and not self.cancelled_at:
            self.cancelled_at = timezone.now()

        super().save(*args, **kwargs)


class OrderHistory(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="history")
    status = models.ForeignKey("OrderStatus", on_delete=models.PROTECT, related_name="history_entries")
    note = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="order_history_entries",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders_order_history"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order.tracking_number} - {self.status.name}"
