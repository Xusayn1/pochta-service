from django.urls import path

from apps.payments.views.v1 import PaymentCreateView, PaymentStatusView

app_name = 'v1'

urlpatterns = [
    path('create/', PaymentCreateView.as_view(), name='payment-create'),
    path('<str:order_number>/status/', PaymentStatusView.as_view(), name='payment-status'),
]
