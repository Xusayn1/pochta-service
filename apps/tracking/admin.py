from django.contrib import admin
from apps.tracking.models import TrackingEvent


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ('order', 'event_type', 'location', 'timestamp', 'created_by')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('order__order_number', 'location')
    readonly_fields = ('timestamp',)
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order',)
        }),
        ('Event Details', {
            'fields': ('event_type', 'location', 'description')
        }),
        ('Metadata', {
            'fields': ('timestamp', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

