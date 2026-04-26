from django.contrib import admin
from django.utils.html import format_html
from apps.orders.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'recipient_name', 'status', 'service_type', 'price', 'created_at', 'tracking_id_display')
    list_filter = ('status', 'service_type', 'created_at', 'to_region')
    search_fields = ('order_number', 'recipient_name', 'recipient_phone')
    readonly_fields = ('order_number', 'price', 'created_at', 'updated_at', 'tracking_preview')
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'sender', 'status')
        }),
        ('Sender Details', {
            'fields': ('sender_address',)
        }),
        ('Recipient Details', {
            'fields': ('recipient_name', 'recipient_phone', 'recipient_address')
        }),
        ('Delivery Info', {
            'fields': ('to_region', 'service_type', 'item_description', 'weight_kg', 'declared_value')
        }),
        ('Pricing', {
            'fields': ('price',)
        }),
        ('Estimates', {
            'fields': ('estimated_delivery',)
        }),
        ('Tracking', {
            'fields': ('tracking_preview',),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def tracking_id_display(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #008000;">{}</span>',
            obj.order_number
        )
    tracking_id_display.short_description = 'Tracking #'
    
    def tracking_preview(self, obj):
        events = obj.tracking_events.all()[:5]
        if not events:
            return "No tracking events yet"
        html = '<ol>'
        for event in events:
            html += f'<li><strong>{event.get_event_type_display()}</strong> - {event.location} ({event.timestamp.strftime("%Y-%m-%d %H:%M")})</li>'
        html += '</ol>'
        return format_html(html)
    tracking_preview.short_description = 'Recent Tracking Events'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing order
            return self.readonly_fields + ['sender']
        return self.readonly_fields

