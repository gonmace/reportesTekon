# Generated by Django 5.2.3 on 2025-07-15 19:23

import django.db.models.deletion
import registrostxtss.models.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrostxtss', '0019_alter_racceso_adicionales'),
    ]

    operations = [
        migrations.CreateModel(
            name='REmpalme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('lat', models.FloatField(validators=[registrostxtss.models.validators.validar_latitud], verbose_name='Latitud Empalme')),
                ('lon', models.FloatField(validators=[registrostxtss.models.validators.validar_longitud], verbose_name='Longitud Empalme')),
                ('proveedor', models.CharField(max_length=100, verbose_name='Proveedor de Energía')),
                ('capacidad', models.CharField(max_length=100, verbose_name='Capacidad de Energía')),
                ('comentarios', models.TextField(blank=True, null=True, verbose_name='Comentarios')),
                ('registro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registrostxtss.registrostxtss', verbose_name='Registro')),
            ],
            options={
                'verbose_name': 'Registro Empalme',
                'verbose_name_plural': 'Registros Empalme',
                'ordering': ['-created_at'],
            },
        ),
    ]
