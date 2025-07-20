"""
Modelos para registros TX/TSS.
"""

from registros.models.base import RegistroBase
from registros.models.paso import PasoBase
from django.db import models
from registros.models.validators import validar_latitud, validar_longitud
from registros.models.completeness_checker import check_model_completeness


class Registros(RegistroBase):
    """
    Modelo para registros TX/TSS.
    """
    class Meta:
        verbose_name = "Registro TX/TSS"
        verbose_name_plural = "Registros TX/TSS"


# Pasos específicos
class RSitio(PasoBase):
    """Paso Sitio para registros TX/TSS."""
    lat = models.FloatField(validators=[validar_latitud], verbose_name='Latitud Inspeccion')
    lon = models.FloatField(validators=[validar_longitud], verbose_name='Longitud Inspeccion')
    altura = models.CharField(max_length=100, verbose_name='Altura Torre')
    dimensiones = models.CharField(max_length=100)
    deslindes = models.CharField(max_length=100)
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Sitio'
        verbose_name_plural = 'Registros Sitio'
    
    @staticmethod
    def get_etapa():
        return 'sitio'
    
    @staticmethod
    def get_actives():
        return RSitio.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(rsitio_id):
        return check_model_completeness(RSitio, rsitio_id)


class RAcceso(PasoBase):
    """Paso Acceso para registros TX/TSS."""
    tipo_suelo = models.CharField(max_length=100, verbose_name='Tipo de Suelo')
    distancia = models.CharField(max_length=100, verbose_name='Distancia')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Acceso'
        verbose_name_plural = 'Registros Acceso'
    
    @staticmethod
    def get_etapa():
        return 'acceso'
    
    @staticmethod
    def get_actives():
        return RAcceso.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(racceso_id):
        return check_model_completeness(RAcceso, racceso_id)


class REmpalme(PasoBase):
    """Paso Empalme para registros TX/TSS."""
    proveedor = models.CharField(max_length=100, verbose_name='Proveedor')
    capacidad = models.CharField(max_length=100, verbose_name='Capacidad')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Empalme'
        verbose_name_plural = 'Registros Empalme'
    
    @staticmethod
    def get_etapa():
        return 'empalme'
    
    @staticmethod
    def get_actives():
        return REmpalme.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(rempalme_id):
        return check_model_completeness(REmpalme, rempalme_id) 