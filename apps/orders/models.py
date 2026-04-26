from decimal import Decimal

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.locations.models import Region
from apps.shared.utils import generate_order_number, calculate_price


class Order(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('standard', 'Standard'),
        ('express', 'Express'),
        ('business', 'Business'),
        ('fragile', 'Fragile'),
        ('freight', 'Freight'),
        ('ecommerce', 'E-commerce'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=20, unique=True, blank=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    sender_address = models.ForeignKey(
        'users.UserAddress',
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True,
        blank=True,
    )
    recipient_name = models.CharField(max_length=255)
    recipient_phone = models.CharField(max_length=20)
    recipient_address = models.TextField()
    item_description = models.CharField(max_length=255, blank=True)
    to_region = models.ForeignKey(Region, on_delete=models.PROTECT, null=True, blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, default='standard')
    weight_kg = models.DecimalField(max_digits=8, decimal_places=2)
    declared_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders_order"
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number or f"Order {self.id}"

    def clean(self):
        super().clean()
        if self.weight_kg is not None and self.weight_kg <= 0:
            raise ValidationError({"weight_kg": "Weight must be greater than zero."})
        if self.declared_value is not None and self.declared_value < 0:
            raise ValidationError({"declared_value": "Declared value cannot be negative."})

    def _generate_unique_order_number(self):
        city_code = (self.to_region.code if self.to_region else "TAS")[:3].upper()
        for _ in range(10):
            candidate = generate_order_number(city_code=city_code)
            if not Order.objects.filter(order_number=candidate).exists():
                return candidate
        raise ValidationError({"order_number": "Unable to generate a unique order number. Please try again."})

    def _apply_defaults(self):
        if not self.order_number:
            self.order_number = self._generate_unique_order_number()

        if self.price in (None, Decimal("0.00"), Decimal("0")):
            self.price = calculate_price(self.service_type, float(self.weight_kg), 100)

        if not self.estimated_delivery and self.to_region:
            delivery_days = max(self.to_region.delivery_days_min, 1)
            self.estimated_delivery = timezone.now() + timezone.timedelta(days=delivery_days)

    def _create_tracking_event(self, event_type, description):
        TrackingEvent = apps.get_model("tracking", "TrackingEvent")
        TrackingEvent.objects.create(
            order=self,
            event_type=event_type,
            location=self.to_region.name_en if self.to_region else "Dispatch center",
            description=description,
        )

    def sync_tracking_history(self, previous_status=None):
        status_events = {
            "pending": ("order_created", "Order created and awaiting confirmation."),
            "confirmed": ("order_created", "Order confirmed and ready for processing."),
            "picked_up": ("picked_up", "Parcel has been picked up."),
            "in_transit": ("in_transit", "Parcel is currently in transit."),
            "out_for_delivery": ("out_for_delivery", "Parcel is out for delivery."),
            "delivered": ("delivered", "Parcel was delivered successfully."),
        }

        event_data = status_events.get(self.status)
        if not event_data:
            return

        event_type, description = event_data
        if previous_status == self.status:
            return

        self._create_tracking_event(event_type=event_type, description=description)

    def save(self, *args, **kwargs):
        previous_status = None
        if self.pk:
            previous_status = (
                Order.objects.filter(pk=self.pk)
                .values_list("status", flat=True)
                .first()
            )

        self.full_clean()
        self._apply_defaults()
        super().save(*args, **kwargs)
        self.sync_tracking_history(previous_status=previous_status)
