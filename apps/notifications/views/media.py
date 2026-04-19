import logging

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.shared.models import Media
from apps.shared.serializers.media import MediaUploadSerializer, MediaDetailSerializer
from apps.shared.utils.custom_paginations import CustomPageNumberPagination
from apps.shared.utils.custom_response import CustomResponse

logger = logging.getLogger(__name__)


class MediaUploadView(APIView):
    """
    POST: Upload a new media file.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MediaUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse.validation_error(
                errors=serializer.errors,
                request=request,
                message_key="MEDIA_FILE_REQUIRED",
            )

        media = serializer.save()
        data = MediaDetailSerializer(media, context={'request': request}).data

        return CustomResponse.success(
            message_key="MEDIA_UPLOADED",
            request=request,
            data=data,
        )


class MediaListView(APIView):
    """
    GET: List all media files with pagination.
    Query params:
        - file_type: filter by IMAGE, VIDEO, DOCUMENT, AUDIO, OTHER
    """

    def get(self, request):
        queryset = Media.objects.all()

        # Optional filter by file_type
        file_type = request.query_params.get('file_type')
        if file_type:
            queryset = queryset.filter(file_type=file_type.upper())

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = MediaDetailSerializer(page, many=True, context={'request': request})
            paginated = paginator.get_paginated_response(serializer.data)
            return CustomResponse.success(
                message_key="SUCCESS",
                request=request,
                data=paginated,
            )

        serializer = MediaDetailSerializer(queryset, many=True, context={'request': request})
        return CustomResponse.success(
            message_key="SUCCESS",
            request=request,
            data=serializer.data,
        )


class MediaDetailView(APIView):
    """
    GET: Retrieve a single media file by uuid.
    DELETE: Delete a media file by uuid.
    """

    def get(self, request, uuid):
        try:
            media = Media.objects.get(uuid=uuid)
        except Media.DoesNotExist:
            return CustomResponse.not_found(
                message_key="MEDIA_NOT_FOUND",
                request=request,
            )

        data = MediaDetailSerializer(media, context={'request': request}).data
        return CustomResponse.success(
            message_key="SUCCESS",
            request=request,
            data=data,
        )

    def delete(self, request, uuid):
        try:
            media = Media.objects.get(uuid=uuid)
        except Media.DoesNotExist:
            return CustomResponse.not_found(
                message_key="MEDIA_NOT_FOUND",
                request=request,
            )

        media.delete()
        return CustomResponse.success(
            message_key="MEDIA_DELETED",
            request=request,
        )