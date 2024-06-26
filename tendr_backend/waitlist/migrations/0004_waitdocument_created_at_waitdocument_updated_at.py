# Generated by Django 4.2.9 on 2024-01-29 18:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("waitlist", "0003_alter_waitdocument_unique_together_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="waitdocument",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="waitdocument",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
