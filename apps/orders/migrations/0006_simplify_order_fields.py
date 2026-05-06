# Generated migration to simplify Order creation

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_order_item_description_order_sender_address'),
    ]

    operations = [
        # Make recipient_name optional
        migrations.AlterField(
            model_name='order',
            name='recipient_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        # Make notes field have a default empty string instead of being required
        migrations.AlterField(
            model_name='order',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),
        # Make service_type have default but allow null
        migrations.AlterField(
            model_name='order',
            name='service_type',
            field=models.CharField(
                blank=True,
                choices=[('standard', 'Standard'), ('express', 'Express'), ('business', 'Business'), ('fragile', 'Fragile'), ('freight', 'Freight'), ('ecommerce', 'E-commerce')],
                default='standard',
                max_length=20
            ),
        ),
        # Make to_region truly optional with NULL allowed
        migrations.AlterField(
            model_name='order',
            name='to_region',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name='orders',
                to='locations.region'
            ),
        ),
    ]
