from django.urls import path, include

app_name = 'shared'

urlpatterns = [
    path('api/v1/', include('apps.shared.urls.v1')),
]