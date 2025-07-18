# Generated by Django 5.2.3 on 2025-07-09 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_site_options_remove_historicalsite_user_and_more'),
        ('registrostxtss', '0003_alter_registrostxtss_sitio'),
        ('users', '0002_alter_user_options'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='registrostxtss',
            constraint=models.UniqueConstraint(condition=models.Q(('registro0', True)), fields=('user',), name='unique_user_with_registro0_true'),
        ),
    ]
