# Generated by Django 5.2.4 on 2025-07-22 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reg_txtss', '0002_remove_historicalregtxtss_deleted_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rsitio',
            name='name',
            field=models.CharField(default='Sitio de Inspección', max_length=100, verbose_name='Nombre del Sitio'),
        ),
    ]
