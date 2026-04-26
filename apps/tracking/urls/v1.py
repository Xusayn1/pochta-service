from django.urls import path

from apps.tracking.views.v1 import AddTrackingEventView, PublicTrackView

app_name = 'v1'

urlpatterns = [
    path('<str:tracking_number>/', PublicTrackView.as_view(), name='public-track'),
    path('<str:tracking_number>/add-event/', AddTrackingEventView.as_view(), name='add-tracking-event'),
]