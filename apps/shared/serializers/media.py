import logging

from rest_framework import serializers

from apps.shared.models import Media

logger = logging.getLogger(__name__)


class MediaUploadSerializer(serializers.Serializer):
    """
    Serializer for uploading a media file.
    Accepts a file and automatically extracts metadata.
    """
    file = serializers.FileField(required=True)

    def validate_file(self, value):
        # Max 50 MB
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size exceeds maximum allowed size ({max_size // (1024 * 1024)} MB)."
            )
        return value

    def create(self, validated_data):
        file = validated_data['file']
        mime_type = getattr(file, 'content_type', '') or ''

        media = Media.objects.create(
            file=file,
            original_name=file.name,
            size=file.size,
            mime_type=mime_type,
            file_type=Media.detect_file_type(mime_type),
        )
        return media


class MediaDetailSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for Media model.
    Use this to nest media data inside other serializers.
    """
    file = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = [
            'id',
            'uuid',
            'file',
            'file_type',
            'original_name',
            'size',
            'mime_type',
            'created_at',
        ]
        read_only_fields = fields

    def get_file(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        elif obj.file:
            return obj.file.url
        return None