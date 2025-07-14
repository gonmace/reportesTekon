from django.db import models
from core.models import BaseModel
from registrostxtss.models.main_registrostxtss import RegistrosTxTss

class RAcceso(BaseModel):
    registro = models.ForeignKey(RegistrosTxTss, on_delete=models.CASCADE, verbose_name='Registro')
    acceso_sitio = models.TextField(max_length=100, verbose_name='Acceso al sitio')
    acceso_sitio_construccion = models.TextField(max_length=100, verbose_name='Acceso al sitio para construcción')
    longitud_acceso_sitio = models.IntegerField(verbose_name='Longitud acceso al Sitio')
    longitud_acceso_construccion = models.IntegerField(verbose_name='Longitud acceso al Sitio para construcción')
    tipo_suelo = models.CharField(max_length=100, verbose_name='Tipo de suelo de sitio y huella')
    obstaculos = models.TextField(max_length=100, verbose_name='Edificaciones cercanas / obstáculos')
    adicionales = models.TextField(max_length=100, verbose_name='Trabajos adicionales a considerar')

    class Meta:
        verbose_name = 'Registro Acceso'
        verbose_name_plural = 'Registros Acceso'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.registro} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    @staticmethod
    def get_etapa():
        return 'acceso'
    
    @staticmethod
    def get_actives():
        return RAcceso.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(racceso_id):
        """
        Verifica si un registro RAcceso tiene todos los campos obligatorios llenos.
        Solo verifica campos que no tienen blank=True y null=True.
        
        Args:
            racceso_id: ID del registro RAcceso
            
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
        # TODO: Verificar si el registro de acceso está relacionado con el registro de sitio
        # Obtener la instancia de RAcceso por ID
        try:
            instance = RAcceso.objects.get(id=racceso_id)
        except RAcceso.DoesNotExist:
            return {
                'color': 'error',
                'is_complete': None,
                'missing_fields': ['racceso_no_encontrado'],
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
