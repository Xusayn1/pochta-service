from django.urls import path

from apps.shipments.views.v1 import AssignCourierView, ShipmentDetailView

app_name = 'v1'

urlpatterns = [
    path('<int:pk>/', ShipmentDetailView.as_view(), name='shipment-detail'),
    path('<int:pk>/assign/', AssignCourierView.as_view(), name='assign-courier'),
]