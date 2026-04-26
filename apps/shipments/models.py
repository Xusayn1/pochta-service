from django.conf import settings
from django.db import models


class Shipment(models.Model):
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='shipment')
    courier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_shipments'
    )
    pickup_address = models.TextField()
    delivery_address = models.TextField()
    pickup_time = models.DateTimeField(null=True, blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)
    distance_km = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    shipment_status = models.CharField(max_length=20, default='pending')
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    dimensions = models.JSONField(default=dict, blank=True)  # {length, width, height}
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shipments_shipment"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Shipment for {self.order.order_number}"

    def save(self, *args, **kwargs):
        # Sync shipment_status with order status
        if self.order:
            self.shipment_status = self.order.status
        super().save(*args, **kwargs)
