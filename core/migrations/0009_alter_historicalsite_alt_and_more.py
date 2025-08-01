# Generated by Django 5.2.4 on 2025-07-23 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_googlemapsimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsite',
            name='alt',
            field=models.IntegerField(blank=True, null=True, verbose_name='Altura (m)'),
        ),
        migrations.AlterField(
            model_name='historicalsite',
            name='lat_base',
            field=models.FloatField(blank=True, db_index=True, null=True, verbose_name='Latitud Mandato'),
        ),
        migrations.AlterField(
            model_name='historicalsite',
            name='lon_base',
            field=models.FloatField(blank=True, db_index=True, null=True, verbose_name='Longitud Mandato'),
        ),
        migrations.AlterField(
            model_name='historicalsite',
            name='name',
            field=models.CharField(db_index=True, max_length=100, verbose_name='Nombre del sitio'),
        ),
        migrations.AlterField(
            model_name='historicalsite',
            name='operator_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Operador ID'),
        ),
        migrations.AlterField(
            model_name='historicalsite',
            name='region',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Región'),
        ),
        migrations.AlterField(
            model_name='site',
            name='alt',
            field=models.IntegerField(blank=True, null=True, verbose_name='Altura (m)'),
        ),
        migrations.AlterField(
            model_name='site',
            name='lat_base',
            field=models.FloatField(blank=True, null=True, unique=True, verbose_name='Latitud Mandato'),
        ),
        migrations.AlterField(
            model_name='site',
            name='lon_base',
            field=models.FloatField(blank=True, null=True, unique=True, verbose_name='Longitud Mandato'),
        ),
        migrations.AlterField(
            model_name='site',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Nombre del sitio'),
        ),
        migrations.AlterField(
            model_name='site',
            name='operator_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Operador ID'),
        ),
        migrations.AlterField(
            model_name='site',
            name='region',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Región'),
        ),
    ]
