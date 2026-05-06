from django.contrib import admin
from .models import Shipment

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'courier', 'shipment_status', 'created_at')
    list_filter = ('shipment_status', 'created_at')
    search_fields = ('order__order_number', 'courier__username', 'courier__full_name')
