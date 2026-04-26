from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import Notification


class NotificationListView(generics.ListAPIView):
    """List notifications for authenticated user"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Disable pagination for now

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MarkReadView(generics.UpdateAPIView):
    """Mark notification as read"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"error": "You can only mark your own notifications as read"},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.is_read = True
        instance.save()
        return Response({"message": "Notification marked as read"})


class ContactMessageSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    service_type = serializers.CharField(max_length=100, required=False, allow_blank=True)
    message = serializers.CharField(required=False, allow_blank=True)


class ContactMessageCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        details = (
            f"Contact request from {payload['full_name']} "
            f"({payload['phone']}, {payload['email']}).\n"
            f"Service: {payload.get('service_type') or 'not specified'}\n"
            f"Message: {payload.get('message') or '-'}"
        )
        Notification.objects.create(
            user=request.user,
            title="Contact form submitted",
            message=details,
            channel="push",
        )
        return Response({"message": "Contact message submitted successfully."}, status=status.HTTP_201_CREATED)