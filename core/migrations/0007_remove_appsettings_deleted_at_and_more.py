# Generated by Django 5.2.4 on 2025-07-22 01:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_appsettings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appsettings',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='registro',
            name='deleted_at',
        ),
    ]
