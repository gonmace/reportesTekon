# Generated by Django 5.2.3 on 2025-07-14 20:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0002_photos_etapa'),
        ('registrostxtss', '0017_delete_registros1'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photos',
            name='registro',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registrostxtss.registrostxtss'),
        ),
    ]
