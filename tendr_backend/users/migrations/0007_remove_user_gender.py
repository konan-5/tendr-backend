# Generated by Django 4.2.9 on 2024-03-10 16:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_rename_birth_of_date_user_birthday"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="gender",
        ),
    ]
