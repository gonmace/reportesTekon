# Generated by Django 5.2.3 on 2025-07-09 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_site_options_remove_historicalsite_user_and_more'),
        ('registrostxtss', '0006_remove_registrostxtss_unique_sitio_with_registro0_true_and_more'),
        ('users', '0002_alter_user_options'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='registrostxtss',
            name='unique_sitio_with_registro0_true',
        ),
        migrations.AddConstraint(
            model_name='registrostxtss',
            constraint=models.UniqueConstraint(fields=('sitio', 'user'), name='unique_sitio_user_combination'),
        ),
    ]
