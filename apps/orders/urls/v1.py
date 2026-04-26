from django.urls import path

from apps.orders.views.v1 import (
    CourierAssignedOrdersView,
    CourierOrderStatusUpdateView,
    OrderCreateView,
    OrderDetailView,
    OrderListView,
)

app_name = 'v1'

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('courier/assigned/', CourierAssignedOrdersView.as_view(), name='courier-assigned-orders'),
    path('courier/<str:order_number>/status/', CourierOrderStatusUpdateView.as_view(), name='courier-order-status-update'),
    path('', OrderListView.as_view(), name='order-list'),
    path('<str:order_number>/', OrderDetailView.as_view(), name='order-detail'),
]