from django.db import migrations, models


def normalize_existing_roles(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(role="client").update(role="user")
    User.objects.filter(role="admin").update(role="manager")


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_alter_user_managers"),
    ]

    operations = [
        migrations.RunPython(normalize_existing_roles, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[("user", "User"), ("courier", "Courier"), ("manager", "Manager")],
                default="user",
                max_length=20,
            ),
        ),
    ]
