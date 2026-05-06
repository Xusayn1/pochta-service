# Generated migration to simplify UserAddress model

from django.db import migrations, models


def migrate_address_data(apps, schema_editor):
    """Migrate existing address data to simplified full_address field."""
    UserAddress = apps.get_model('users', 'UserAddress')
    
    for address in UserAddress.objects.all():
        # Combine existing fields into full_address
        parts = []
        if address.title:
            parts.append(address.title)
        if hasattr(address, 'city') and address.city and hasattr(address.city, 'name_en'):
            parts.append(address.city.name_en)
        if address.address:
            parts.append(address.address)
        if address.landmark:
            parts.append(address.landmark)
        
        full_address = ", ".join(parts)
        address.full_address = full_address
        address.save(update_fields=['full_address'])


def reverse_migrate(apps, schema_editor):
    """Reverse migration - clear full_address field."""
    UserAddress = apps.get_model('users', 'UserAddress')
    UserAddress.objects.all().update(full_address='')


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_normalize_user_roles'),
    ]

    operations = [
        # Add the new full_address field
        migrations.AddField(
            model_name='useraddress',
            name='full_address',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        # Run data migration
        migrations.RunPython(migrate_address_data, reverse_migrate),
        # Remove the old foreign keys and fields
        migrations.RemoveField(
            model_name='useraddress',
            name='region',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='city',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='address',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='landmark',
        ),
    ]
