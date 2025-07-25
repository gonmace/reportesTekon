"""
Modelos para registros Instalación.
"""

from registros.models.base import RegistroBase
from registros.models.paso import PasoBase
from django.db import models
from registros.models.validators import validar_latitud, validar_longitud
from registros.models.completeness_checker import check_model_completeness
from core.models.sites import Site
from users.models import User
from simple_history.models import HistoricalRecords

class RegInstalacion(RegistroBase):
    """
    Modelo para registros Instalación.
    """
    sitio = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Sitio', related_name='reg_instalacion')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario', related_name='reg_instalacion')
    title = models.CharField(max_length=100, verbose_name='Título')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"RegInstalacion {self.id}"
    
    def clean(self):
        """Custom validation method"""
        super().clean()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs) 


class Sitio(PasoBase):
    """Paso Sitio para registros Instalación."""
    registro = models.ForeignKey(RegInstalacion, on_delete=models.CASCADE, verbose_name='Registro')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Sitio'
        verbose_name_plural = 'Registros Sitio'
    
    @staticmethod
    def get_etapa():
        return 'sitio'
    
    @staticmethod
    def get_actives():
        return Sitio.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(sitio_id):
        return check_model_completeness(Sitio, sitio_id)


class Acceso(PasoBase):
    """Paso Acceso para registros Instalación."""
    registro = models.ForeignKey(RegInstalacion, on_delete=models.CASCADE, verbose_name='Registro')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Acceso'
        verbose_name_plural = 'Registros Acceso'
    
    @staticmethod
    def get_etapa():
        return 'acceso'
    
    @staticmethod
    def get_actives():
        return Acceso.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(acceso_id):
        return check_model_completeness(Acceso, acceso_id)


class Empalme(PasoBase):
    """Paso Empalme para registros Instalación."""
    registro = models.ForeignKey(RegInstalacion, on_delete=models.CASCADE, verbose_name='Registro')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Empalme'
        verbose_name_plural = 'Registros Empalme'
    
    @staticmethod
    def get_etapa():
        return 'empalme'
    
    @staticmethod
    def get_actives():
        return Empalme.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(empalme_id):
        return check_model_completeness(Empalme, empalme_id)

