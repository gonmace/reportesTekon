from django.db import models
from django.utils import timezone
from users.models import User
from core.models.sites import Site
from core.models import BaseModel
from registrostxtss.models.validators import validar_latitud, validar_longitud
from registrostxtss.models.main_registrostxtss import RegistrosTxTss

class RSitio(BaseModel):
    registro = models.ForeignKey(RegistrosTxTss, on_delete=models.CASCADE, verbose_name='Registro')
    lat = models.FloatField(validators=[validar_latitud], verbose_name='Latitud Inspeccion')
    lon = models.FloatField(validators=[validar_longitud], verbose_name='Longitud Inspeccion')
    altura = models.CharField(max_length=100, verbose_name='Altura Torre')
    dimensiones = models.CharField(max_length=100)
    deslindes = models.CharField(max_length=100)
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Sitio'
        verbose_name_plural = 'Registros Sitio'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.registro} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    @staticmethod
    def get_table():
        return 'registros0'
    
    @staticmethod
    def get_actives():
        return RSitio.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(rsitio_id):
        """
        Verifica si un registro RSitio tiene todos los campos obligatorios llenos.
        Solo verifica campos que no tienen blank=True y null=True.
        
        Args:
            rsitio_id: ID del registro RSitio
            
        Returns:
            dict: Diccionario con información sobre la completitud del registro
                {
                    'color': str,
                    'is_complete': bool,
                    'missing_fields': list,
                    'total_fields': int,
                    'filled_fields': int
                }
        """
        # Obtener la instancia de RSitio por ID
        try:
            instance = RSitio.objects.get(id=rsitio_id)
        except RSitio.DoesNotExist:
            return {
                'color': 'error',
                'is_complete': None,
                'missing_fields': ['rsitio_no_encontrado'],
                'total_fields': 0,
                'filled_fields': 0
            }
        
        missing_fields = []
        
        # Obtener todos los campos del modelo
        fields = instance._meta.get_fields()
        
        for field in fields:
            # Solo verificar campos que no son automáticos y no tienen blank=True y null=True
            if (hasattr(field, 'blank') and hasattr(field, 'null') and 
                 field.blank and field.null and field.name != 'deleted_at'):
                
                field_value = getattr(instance, field.name, None)
                
                # Verificar si el campo está vacío
                if field_value is None or (isinstance(field_value, str) and field_value.strip() == ''):
                    missing_fields.append(field.name)
        
        total_fields = len([f for f in fields if hasattr(f, 'blank') and hasattr(f, 'null') and not f.blank and not f.null and not f.auto_created and not f.is_relation])
        filled_fields = total_fields - len(missing_fields)
        
        return {
            'color': 'warning' if len(missing_fields) > 0 else 'success',
            'is_complete': len(missing_fields) == 0,
            'missing_fields': missing_fields,
            'total_fields': total_fields,
            'filled_fields': filled_fields
        }
