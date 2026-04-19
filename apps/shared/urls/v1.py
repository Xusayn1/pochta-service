from django.urls import path

from apps.shared.views.media import MediaUploadView, MediaListView, MediaDetailView

app_name = 'shared'

urlpatterns = [
    path('media/', MediaListView.as_view(), name='media-list'),
    path('media/upload/', MediaUploadView.as_view(), name='media-upload'),
    path('media/<uuid:uuid>/', MediaDetailView.as_view(), name='media-detail'),
]