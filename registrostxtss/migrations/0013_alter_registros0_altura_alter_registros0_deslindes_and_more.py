# Generated by Django 5.2.3 on 2025-07-12 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrostxtss', '0012_registros0_comentarios'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registros0',
            name='altura',
            field=models.CharField(max_length=100, verbose_name='Altura Torre'),
        ),
        migrations.AlterField(
            model_name='registros0',
            name='deslindes',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='registros0',
            name='dimensiones',
            field=models.CharField(max_length=100),
        ),
    ]
