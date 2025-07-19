from django.db import models
from core.models import BaseModel
from registros.models.validators import validar_latitud, validar_longitud
from registros.models.registrostxtss import Registros
from registros.models.completeness_checker import check_model_completeness

class REmpalme(BaseModel):
    registro = models.ForeignKey(Registros, on_delete=models.CASCADE, verbose_name='Registro')
    lat = models.FloatField(validators=[validar_latitud], verbose_name='Latitud Empalme')
    lon = models.FloatField(validators=[validar_longitud], verbose_name='Longitud Empalme')
    proveedor = models.CharField(max_length=100, verbose_name='Proveedor de Energía')
    capacidad = models.CharField(max_length=100, verbose_name='Capacidad de Energía')
    no_poste = models.CharField(blank=True, null=True, max_length=100, verbose_name='No. Poste')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Empalme'
        verbose_name_plural = 'Registros Empalme'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.registro} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    @staticmethod
    def get_etapa():
        return 'empalme'
    
    @staticmethod
    def get_actives():
        return REmpalme.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(rempalme_id):
        """
        Verifica si un registro REmpalme tiene todos los campos obligatorios llenos.
        Solo verifica campos que no tienen blank=True y null=True.
        
        Args:
            rempalme_id: ID del registro REmpalme
            
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
        return check_model_completeness(REmpalme, rempalme_id)
