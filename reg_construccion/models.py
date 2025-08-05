"""
Modelos para registros Reporte de construcción.
"""

from registros.models.base import RegistroBase
from registros.models.paso import PasoBase
from django.db import models
from registros.models.validators import validar_latitud, validar_longitud
from registros.models.completeness_checker import check_model_completeness
from core.models.sites import Site
from users.models import User
from proyectos.models import Grupo, Componente, GrupoComponente
from simple_history.models import HistoricalRecords
from datetime import date

class RegConstruccion(RegistroBase):
    """
    Modelo para registros Reporte de construcción.
    """
    sitio = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Sitio', related_name='reg_construccion')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario', related_name='reg_construccion')
    estructura = models.ForeignKey(Grupo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Estructura', related_name='reg_construccion')
    title = models.CharField(max_length=100, verbose_name='Título')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"RegConstruccion {self.id}"
    
    def clean(self):
        """Custom validation method"""
        super().clean()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs) 


class Visita(PasoBase):
    """Paso Visita para registros Reporte de construcción."""
    registro = models.ForeignKey(RegConstruccion, on_delete=models.CASCADE, verbose_name='Registro')
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
    """Paso Avance para registros Reporte de construcción."""
    registro = models.ForeignKey(RegConstruccion, on_delete=models.CASCADE, verbose_name='Registro')
    fecha = models.DateField(verbose_name='Fecha del avance', default=date.today)
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    porcentaje_avance = models.IntegerField(
        verbose_name='Porcentaje de avance', 
        default=0,
        help_text='Porcentaje de avance del 0 al 100'
    )
    
    class Meta:
        verbose_name = 'Registro Avance'
        verbose_name_plural = 'Registros Avance'
        ordering = ['-fecha', '-created_at']
    
    @staticmethod
    def get_etapa():
        return 'avance'
    
    @staticmethod
    def get_actives():
        return Avance.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(avance_id):
        return check_model_completeness(Avance, avance_id)
    
    def clean(self):
        """Validación personalizada para el porcentaje de avance"""
        super().clean()
        if self.porcentaje_avance < 0 or self.porcentaje_avance > 100:
            from django.core.exceptions import ValidationError
            raise ValidationError('El porcentaje de avance debe estar entre 0 y 100')


class AvanceComponente(PasoBase):
    """
    Avance específico por componente de la estructura del proyecto.
    Permite registrar el progreso actual y acumulado de cada componente.
    """
    registro = models.ForeignKey(RegConstruccion, on_delete=models.CASCADE, verbose_name='Registro')
    fecha = models.DateField(verbose_name='Fecha del avance', default=date.today)
    componente = models.ForeignKey(
        Componente, 
        on_delete=models.CASCADE, 
        verbose_name='Componente',
        related_name='avances_componente'
    )
    porcentaje_actual = models.IntegerField(
        verbose_name='Porcentaje actual', 
        default=0,
        help_text='Porcentaje de avance actual del componente (0-100)'
    )
    porcentaje_acumulado = models.IntegerField(
        verbose_name='Porcentaje acumulado', 
        default=0,
        help_text='Porcentaje de avance acumulado del componente (0-100)'
    )
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Avance por Componente'
        verbose_name_plural = 'Avances por Componente'
        ordering = ['-fecha', '-created_at']
        unique_together = ['registro', 'componente', 'fecha']
    
    @staticmethod
    def get_etapa():
        return 'avance_componente'
    
    @staticmethod
    def get_actives():
        return AvanceComponente.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(avance_componente_id):
        return check_model_completeness(AvanceComponente, avance_componente_id)
    
    def clean(self):
        """Validación personalizada para los porcentajes"""
        super().clean()
        if self.porcentaje_actual < 0 or self.porcentaje_actual > 100:
            from django.core.exceptions import ValidationError
            raise ValidationError('El porcentaje actual debe estar entre 0 y 100')
        
        if self.porcentaje_acumulado < 0 or self.porcentaje_acumulado > 100:
            from django.core.exceptions import ValidationError
            raise ValidationError('El porcentaje acumulado debe estar entre 0 y 100')
        
        if self.porcentaje_acumulado < self.porcentaje_actual:
            from django.core.exceptions import ValidationError
            raise ValidationError('El porcentaje acumulado no puede ser menor al porcentaje actual')
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para calcular automáticamente el porcentaje acumulado si no se especifica"""
        if not self.porcentaje_acumulado:
            # Obtener el último avance acumulado para este componente
            ultimo_avance = AvanceComponente.objects.filter(
                registro=self.registro,
                componente=self.componente
            ).exclude(id=self.id).order_by('-fecha', '-created_at').first()
            
            if ultimo_avance:
                self.porcentaje_acumulado = max(ultimo_avance.porcentaje_acumulado, self.porcentaje_actual)
            else:
                self.porcentaje_acumulado = self.porcentaje_actual
        
        super().save(*args, **kwargs)

