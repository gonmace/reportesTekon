"""
Modelos para registros Mantenimiento Preventivo.
"""

from registros.models.base import RegistroBase
from registros.models.paso import PasoBase
from django.db import models
from registros.models.validators import validar_latitud, validar_longitud
from registros.models.completeness_checker import check_model_completeness
from core.models.sites import Site
from users.models import User
from simple_history.models import HistoricalRecords

class RegMantenimiento(RegistroBase):
    """
    Modelo para registros Mantenimiento Preventivo.
    """
    sitio = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Sitio', related_name='reg_mantenimiento')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario', related_name='reg_mantenimiento')
    title = models.CharField(max_length=100, verbose_name='Título')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"RegMantenimiento {self.id}"
    
    def clean(self):
        """Custom validation method"""
        super().clean()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs) 


class Inspeccion(PasoBase):
    """Paso Inspeccion para registros Mantenimiento Preventivo."""
    registro = models.ForeignKey(RegMantenimiento, on_delete=models.CASCADE, verbose_name='Registro')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Inspeccion'
        verbose_name_plural = 'Registros Inspeccion'
    
    @staticmethod
    def get_etapa():
        return 'inspeccion'
    
    @staticmethod
    def get_actives():
        return Inspeccion.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(inspeccion_id):
        return check_model_completeness(Inspeccion, inspeccion_id)


class Diagnostico(PasoBase):
    """Paso Diagnostico para registros Mantenimiento Preventivo."""
    registro = models.ForeignKey(RegMantenimiento, on_delete=models.CASCADE, verbose_name='Registro')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Diagnostico'
        verbose_name_plural = 'Registros Diagnostico'
    
    @staticmethod
    def get_etapa():
        return 'diagnostico'
    
    @staticmethod
    def get_actives():
        return Diagnostico.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(diagnostico_id):
        return check_model_completeness(Diagnostico, diagnostico_id)


class Reparacion(PasoBase):
    """Paso Reparacion para registros Mantenimiento Preventivo."""
    registro = models.ForeignKey(RegMantenimiento, on_delete=models.CASCADE, verbose_name='Registro')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Reparacion'
        verbose_name_plural = 'Registros Reparacion'
    
    @staticmethod
    def get_etapa():
        return 'reparacion'
    
    @staticmethod
    def get_actives():
        return Reparacion.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(reparacion_id):
        return check_model_completeness(Reparacion, reparacion_id)


class Pruebas(PasoBase):
    """Paso Pruebas para registros Mantenimiento Preventivo."""
    registro = models.ForeignKey(RegMantenimiento, on_delete=models.CASCADE, verbose_name='Registro')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Pruebas'
        verbose_name_plural = 'Registros Pruebas'
    
    @staticmethod
    def get_etapa():
        return 'pruebas'
    
    @staticmethod
    def get_actives():
        return Pruebas.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(pruebas_id):
        return check_model_completeness(Pruebas, pruebas_id)


class Verificacion(PasoBase):
    """Paso Verificacion para registros Mantenimiento Preventivo."""
    registro = models.ForeignKey(RegMantenimiento, on_delete=models.CASCADE, verbose_name='Registro')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Verificacion'
        verbose_name_plural = 'Registros Verificacion'
    
    @staticmethod
    def get_etapa():
        return 'verificacion'
    
    @staticmethod
    def get_actives():
        return Verificacion.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(verificacion_id):
        return check_model_completeness(Verificacion, verificacion_id)

