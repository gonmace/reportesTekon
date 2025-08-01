# Generated by Django 5.2.4 on 2025-07-21 20:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('object_id', models.PositiveIntegerField()),
                ('etapa', models.CharField(max_length=255)),
                ('imagen', models.ImageField(upload_to='photos/')),
                ('descripcion', models.CharField(blank=True, max_length=128, null=True)),
                ('orden', models.IntegerField(default=0)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Foto',
                'verbose_name_plural': 'Fotos',
                'ordering': ['orden', '-created_at'],
            },
        ),
    ]
