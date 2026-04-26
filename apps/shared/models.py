import mimetypes
import os
import uuid

from django.db import models
from django.conf import settings


class Language(models.TextChoices):
    RU = "RU", "Russian"
    EN = "EN", "English"
    CRL = "CRL", "Cyrillic"
    UZ = "UZ", "Uzbek"


class DeviceTheme(models.TextChoices):
    DARK = "DARK", "Dark"
    LIGHT = "LIGHT", "Light"


class DeviceType(models.TextChoices):
    IOS = "IOS", "iOS"
    ANDROID = "ANDROID", "Android"
    ALL = "ALL", "ALL"


class BaseModel(models.Model):
    """
    Abstract base model with UUID primary key and timestamp fields
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


def media_upload_path(instance, filename):
    """
    Generate upload path: uploads/<file_type>/YYYY/MM/<uuid>_<filename>
    Example: uploads/image/2026/04/a1b2c3d4_photo.jpg
    """
    from django.utils import timezone
    now = timezone.now()
    ext = os.path.splitext(filename)[1]
    unique_name = f"{instance.uuid}{ext}"
    return f"uploads/{instance.file_type.lower()}/{now.year}/{now.month:02d}/{unique_name}"


class Media(BaseModel):
    """
    Reusable media model for storing all kinds of files.
    Any model in the project can ForeignKey or ManyToMany to this.

    Usage:
        thumbnail = models.ForeignKey('shared.Media', on_delete=models.SET_NULL, null=True)
        gallery = models.ManyToManyField('shared.Media', blank=True)
    """

    class FileType(models.TextChoices):
        IMAGE = 'IMAGE', 'Image'
        VIDEO = 'VIDEO', 'Video'
        DOCUMENT = 'DOCUMENT', 'Document'
        AUDIO = 'AUDIO', 'Audio'
        OTHER = 'OTHER', 'Other'

    # Map common MIME prefixes to FileType
    MIME_TYPE_MAP = {
        'image': FileType.IMAGE,
        'video': FileType.VIDEO,
        'audio': FileType.AUDIO,
        'application/pdf': FileType.DOCUMENT,
        'application/msword': FileType.DOCUMENT,
        'application/vnd.': FileType.DOCUMENT,
        'text': FileType.DOCUMENT,
    }

    file = models.FileField(upload_to=media_upload_path)
    file_type = models.CharField(
        max_length=20,
        choices=FileType,
        default=FileType.OTHER,
        db_index=True
    )
    original_name = models.CharField(max_length=512)
    size = models.PositiveBigIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        db_table = 'media'
        verbose_name = 'Media'
        verbose_name_plural = 'Media'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.original_name} ({self.file_type})"

    @classmethod
    def detect_file_type(cls, mime_type: str) -> str:
        """Detect FileType from MIME type string."""
        if not mime_type:
            return cls.FileType.OTHER

        mime_lower = mime_type.lower()
        for prefix, file_type in cls.MIME_TYPE_MAP.items():
            if mime_lower.startswith(prefix):
                return file_type
        return cls.FileType.OTHER

    def save(self, *args, **kwargs):
        if self.file:
            if not self.original_name:
                self.original_name = os.path.basename(self.file.name)

            detected_size = getattr(self.file, 'size', None)
            if detected_size is not None:
                self.size = detected_size

            if not self.mime_type:
                guessed_mime_type, _ = mimetypes.guess_type(self.file.name)
                self.mime_type = guessed_mime_type or ''

            if not self.file_type or self.file_type == self.FileType.OTHER:
                self.file_type = self.detect_file_type(self.mime_type)

        super().save(*args, **kwargs)


class Onboarding(models.Model):
    """
    Onboarding model for user onboarding process
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='onboarding')
    completed_steps = models.JSONField(default=dict, help_text="JSON object of completed onboarding steps")
    is_completed = models.BooleanField(default=False)

    class Meta:
        db_table = 'onboarding'
        verbose_name = 'Onboarding'
        verbose_name_plural = 'Onboardings'

    def __str__(self):
        return f"Onboarding for {self.user}"


class FAQ(models.Model):
    """
    Frequently Asked Questions model
    """
    question = models.CharField(max_length=500)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'faqs'
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question
