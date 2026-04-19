import logging

from django.db.models.signals import post_delete
from django.dispatch import receiver

from apps.shared.models import Media

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Media)
def delete_media_file_on_model_delete(sender, instance, **kwargs):
    """
    Delete the physical file from storage after the Media DB record is deleted.

    Uses post_delete (not pre_delete) so the file is only removed
    after the DB deletion succeeds. Works with both:
        - instance.delete()
        - Media.objects.filter(...).delete()  (bulk)
    """
    if instance.file and instance.file.name:
        try:
            storage = instance.file.storage
            if storage.exists(instance.file.name):
                storage.delete(instance.file.name)
                logger.info(f"Deleted file: {instance.file.name}")
        except Exception as e:
            logger.error(f"Failed to delete file {instance.file.name}: {e}")