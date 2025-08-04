"""
Modelos para registros Reporte de visita.
"""

from registros.models.base import RegistroBase
from registros.models.paso import PasoBase
from django.db import models
from registros.models.validators import validar_latitud, validar_longitud
from registros.models.completeness_checker import check_model_completeness
from core.models.sites import Site
from users.models import User
from proyectos.models import Grupo
from simple_history.models import HistoricalRecords

class RegVisita(RegistroBase):
    """
    Modelo para registros Reporte de visita.
    """
    sitio = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Sitio', related_name='reg_visita')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario', related_name='reg_visita')
    estructura = models.ForeignKey(Grupo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Estructura', related_name='reg_visita')
    title = models.CharField(max_length=100, verbose_name='Título')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"RegVisita {self.id}"
    
    def clean(self):
        """Custom validation method"""
        super().clean()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs) 


class Visita(PasoBase):
    """Paso Visita para registros Reporte de visita."""
    registro = models.ForeignKey(RegVisita, on_delete=models.CASCADE, verbose_name='Registro')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Visita'
        verbose_name_plural = 'Registros Visita'
    
    @staticmethod
    def get_etapa():
        return 'visita'
    
    @staticmethod
    def get_actives():
        return Visita.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(visita_id):
        return check_model_completeness(Visita, visita_id)


class Avance(PasoBase):
    """Paso Avance para registros Reporte de visita."""
    registro = models.ForeignKey(RegVisita, on_delete=models.CASCADE, verbose_name='Registro')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Avance'
        verbose_name_plural = 'Registros Avance'
    
    @staticmethod
    def get_etapa():
        return 'avance'
    
    @staticmethod
    def get_actives():
        return Avance.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(avance_id):
        return check_model_completeness(Avance, avance_id)

