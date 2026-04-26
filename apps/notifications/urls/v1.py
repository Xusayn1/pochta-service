from django.urls import path

from apps.notifications.views.v1 import ContactMessageCreateView, MarkReadView, NotificationListView

app_name = 'v1'

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('contact/', ContactMessageCreateView.as_view(), name='contact-message-create'),
    path('<int:pk>/read/', MarkReadView.as_view(), name='mark-read'),
]