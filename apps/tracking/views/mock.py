from django.http import JsonResponse

from apps.orders.models import Order
from apps.tracking.models import TrackingEvent


def mock_track_parcel(request):
    tracking_number = request.GET.get('tracking_number')
    phone = request.GET.get('phone')

    if not tracking_number:
        return JsonResponse({"error": "tracking_number query parameter is required"}, status=400)

    if len(tracking_number) < 5:
        return JsonResponse({"error": "Invalid tracking number. Must be at least 5 characters long."}, status=400)

    # Look up the real order
    try:
        order = Order.objects.select_related('to_region').get(order_number=tracking_number)
    except Order.DoesNotExist:
        return JsonResponse({"error": "Tracking number not found."}, status=404)

    # Build a human-readable status label
    STATUS_LABELS = {
        "pending": "Qabul qilindi",
        "confirmed": "Qabul qilindi",
        "picked_up": "Yuk olib ketildi",
        "in_transit": "Yo'lda",
        "out_for_delivery": "Etkazishga yuborildi",
        "delivered": "Etkazildi",
        "cancelled": "Bekor qilingan",
    }
    status_label = STATUS_LABELS.get(order.status, order.status)

    # Fetch real tracking events ordered oldest → newest
    events = TrackingEvent.objects.filter(order=order).order_by('timestamp')
    history = []
    for event in events:
        event_label = STATUS_LABELS.get(event.event_type, event.event_type.replace("_", " ").title())
        history.append({
            "step": event_label,
            "date": event.timestamp.strftime("%Y-%m-%d %H:%M"),
            "description": event.description,
            "location": event.location,
        })

    # ETA
    eta = order.estimated_delivery.strftime("%Y-%m-%d") if order.estimated_delivery else "N/A"

    return JsonResponse({
        "tracking_number": order.order_number,
        "status": status_label,
        "eta": eta,
        "phone_provided": bool(phone),
        "recipient_name": order.recipient_name,
        "service_type": order.service_type,
        "history": history,
    })
