"""
Modelos para el manejo de componentes (items) y grupos.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Componente(models.Model):
    """
    Componentes (items/actividades) reutilizables.
    Cada componente es una actividad específica que puede ser usada en diferentes grupos.
    Ejemplo: "Instalación de faenas", "Replanteo y Trazado", "Excavación"
    """
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Componente")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    
    class Meta:
        verbose_name = "Componente"
        verbose_name_plural = "Componentes"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Grupo(models.Model):
    """
    Grupos que agrupan componentes (items) relacionados con sus pesos.
    Ejemplo: "Torres" puede agrupar todos los componentes, "Torres pequeñas" solo la mitad.
    """
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Grupo")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre
    
    @property
    def porcentaje_incidencia_total(self):
        """Calcula el porcentaje total de incidencia de todos los componentes del grupo."""
        return sum(gc.porcentaje_incidencia for gc in self.componentes_grupo.filter(activo=True))
    



class GrupoComponente(models.Model):
    """
    Modelo intermedio para relacionar grupos con componentes y asignar pesos.
    Permite que el mismo componente tenga diferentes pesos en diferentes grupos.
    """
    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.CASCADE,
        related_name='componentes_grupo',
        verbose_name="Grupo"
    )
    componente = models.ForeignKey(
        Componente,
        on_delete=models.CASCADE,
        related_name='grupos_componente',
        verbose_name="Componente"
    )
    porcentaje_incidencia = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="% Incidencia",
        help_text="Porcentaje de peso del componente en este grupo"
    )
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Componente de Grupo"
        verbose_name_plural = "Componentes de Grupo"
        ordering = ['orden']
        unique_together = ['grupo', 'componente']
    
    def __str__(self):
        return f"{self.grupo.nombre} - {self.componente.nombre} ({self.porcentaje_incidencia}%)"
