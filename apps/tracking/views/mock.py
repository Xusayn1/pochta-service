from django.http import JsonResponse
import time

def mock_track_parcel(request):
    tracking_number = request.GET.get('tracking_number')
    phone = request.GET.get('phone')

    if not tracking_number:
        return JsonResponse({"error": "tracking_number query parameter is required"}, status=400)

    # Basic validation for the mock
    if len(tracking_number) < 5:
        return JsonResponse({"error": "Invalid tracking number. Must be at least 5 characters long."}, status=400)

    # Return mock data
    return JsonResponse({
        "tracking_number": tracking_number,
        "status": "In Transit",
        "eta": "2026-04-23",
        "phone_provided": bool(phone),
        "history": [
            {"step": "Order Confirmed", "date": "2026-04-20 10:00"},
            {"step": "Picked Up", "date": "2026-04-21 14:30"},
            {"step": "In Transit", "date": "2026-04-22 09:15"}
        ]
    })
