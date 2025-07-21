from django.db import models
from core.models import BaseModel
from registros.models.registrostxtss import Registros
from registros.models.completeness_checker import check_model_completeness


class RSitio(BaseModel):
    registro = models.ForeignKey(Registros, on_delete=models.CASCADE, verbose_name='Registro')
    lat = models.DecimalField(max_digits=10, decimal_places=8, verbose_name='Latitud', help_text='ej: -33.432611')
    lon = models.DecimalField(max_digits=11, decimal_places=8, verbose_name='Longitud', help_text='ej: -70.669261')
    dimensiones = models.CharField(max_length=50, verbose_name='Dimensiones del sitio', help_text='ej: 15x15 m')
    altura = models.CharField(max_length=100, verbose_name='Altura', help_text='ej: 18 / 18 +50 / +100 m')
    deslindes = models.TextField(max_length=200, verbose_name='Deslindes', help_text='Distancia a los bordes de la propiedad')
    comentarios = models.TextField(max_length=500, blank=True, null=True, verbose_name='Comentarios')
    
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
        return check_model_completeness(RSitio, rsitio_id) 