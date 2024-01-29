# Generated by Django 4.2.9 on 2024-01-29 18:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("scrape", "0001_initial"),
        ("waitlist", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WaitDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tendr_id", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="scrape.tender")),
                (
                    "user_id",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
