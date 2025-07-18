from django.db import models
from core.models import BaseModel
from registrostxtss.models.validators import validar_latitud, validar_longitud
from registrostxtss.models.registrostxtss import RegistrosTxTss
from registrostxtss.models.completeness_checker import check_model_completeness


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
    def get_etapa():
        return 'sitio'
    
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
        return check_model_completeness(RSitio, rsitio_id)

