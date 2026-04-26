from django.conf import settings
from django.db import models


class TrackingEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('order_created', 'Order Created'),
        ('picked_up', 'Picked Up'),
        ('hub_arrival', 'Hub Arrival'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed_attempt', 'Failed Attempt'),
    ]

    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='tracking_events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    location = models.CharField(max_length=255)  # City/hub name
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tracking_events'
    )

    class Meta:
        db_table = "tracking_trackingevent"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.order.order_number} - {self.event_type} at {self.location}"
