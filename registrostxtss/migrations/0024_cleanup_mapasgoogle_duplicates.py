# Generated manually to clean up duplicate MapasGoogle records

from django.db import migrations, models


def cleanup_duplicates(apps, schema_editor):
    """
    Clean up duplicate MapasGoogle records by keeping only the most recent one
    for each registro-etapa combination
    """
    MapasGoogle = apps.get_model('registrostxtss', 'MapasGoogle')
    
    # Get all registro-etapa combinations that have duplicates
    from django.db.models import Count
    duplicates = MapasGoogle.objects.values('registro', 'etapa').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    for duplicate in duplicates:
        registro_id = duplicate['registro']
        etapa = duplicate['etapa']
        
        # Get all records for this combination, ordered by fecha_creacion (newest first)
        records = MapasGoogle.objects.filter(
            registro_id=registro_id,
            etapa=etapa
        ).order_by('-fecha_creacion')
        
        # Keep the first (most recent) record, delete the rest
        records_to_delete = records[1:]
        for record in records_to_delete:
            # Delete the physical file if it exists
            if record.archivo:
                try:
                    from django.core.files.storage import default_storage
                    if default_storage.exists(record.archivo.name):
                        default_storage.delete(record.archivo.name)
                except Exception:
                    # If there's an error deleting the file, continue
                    pass
            
            # Delete the database record
            record.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('registrostxtss', '0023_mapasgoogle_delete_mapadesfase'),
    ]

    operations = [
        # First, clean up duplicates
        migrations.RunPython(cleanup_duplicates, reverse_code=migrations.RunPython.noop),
        
        # Then add the unique constraint
        migrations.AddConstraint(
            model_name='mapasgoogle',
            constraint=models.UniqueConstraint(
                fields=['registro', 'etapa'],
                name='unique_registro_etapa_combination'
            ),
        ),
    ] 