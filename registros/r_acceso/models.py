from django.db import models
from core.models import BaseModel
from registros.models.registrostxtss import Registros
from registros.models.completeness_checker import check_model_completeness


class RAcceso(BaseModel):
    registro = models.ForeignKey(Registros, on_delete=models.CASCADE, verbose_name='Registro')
    acceso_sitio = models.TextField(max_length=100, verbose_name='Acceso al sitio')
    acceso_sitio_construccion = models.TextField(max_length=100, verbose_name='Acceso al sitio para construcción')
    longitud_acceso_sitio = models.IntegerField(verbose_name='Longitud acceso al Sitio')
    longitud_acceso_construccion = models.IntegerField(verbose_name='Longitud acceso al Sitio para construcción')
    tipo_suelo = models.CharField(max_length=100, verbose_name='Tipo de suelo de sitio y huella')
    obstaculos = models.TextField(max_length=100, verbose_name='Edificaciones cercanas / obstáculos')
    adicionales = models.TextField(max_length=100, blank=True, null=True, verbose_name='Trabajos adicionales a considerar')
    
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
        return check_model_completeness(RAcceso, racceso_id) 