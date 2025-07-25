"""
Modelos para registros Test Completo.
"""

from registros.models.base import RegistroBase
from registros.models.paso import PasoBase
from django.db import models
from registros.models.validators import validar_latitud, validar_longitud
from registros.models.completeness_checker import check_model_completeness
from core.models.sites import Site
from users.models import User
from simple_history.models import HistoricalRecords

class RegTestCompleto(RegistroBase):
    """
    Modelo para registros Test Completo.
    """
    sitio = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Sitio', related_name='reg_test_completo')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario', related_name='reg_test_completo')
    title = models.CharField(max_length=100, verbose_name='Título')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"RegTestCompleto {self.id}"
    
    def clean(self):
        """Custom validation method"""
        super().clean()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs) 


class Paso1(PasoBase):
    """Paso Paso1 para registros Test Completo."""
    registro = models.ForeignKey(RegTestCompleto, on_delete=models.CASCADE, verbose_name='Registro')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Paso1'
        verbose_name_plural = 'Registros Paso1'
    
    @staticmethod
    def get_etapa():
        return 'paso1'
    
    @staticmethod
    def get_actives():
        return Paso1.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(paso1_id):
        return check_model_completeness(Paso1, paso1_id)


class Paso2(PasoBase):
    """Paso Paso2 para registros Test Completo."""
    registro = models.ForeignKey(RegTestCompleto, on_delete=models.CASCADE, verbose_name='Registro')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Paso2'
        verbose_name_plural = 'Registros Paso2'
    
    @staticmethod
    def get_etapa():
        return 'paso2'
    
    @staticmethod
    def get_actives():
        return Paso2.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(paso2_id):
        return check_model_completeness(Paso2, paso2_id)


class Paso3(PasoBase):
    """Paso Paso3 para registros Test Completo."""
    registro = models.ForeignKey(RegTestCompleto, on_delete=models.CASCADE, verbose_name='Registro')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Paso3'
        verbose_name_plural = 'Registros Paso3'
    
    @staticmethod
    def get_etapa():
        return 'paso3'
    
    @staticmethod
    def get_actives():
        return Paso3.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(paso3_id):
        return check_model_completeness(Paso3, paso3_id)

