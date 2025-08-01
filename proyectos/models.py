from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models.sites import Site
from users.models import User
from simple_history.models import HistoricalRecords

class Componente(models.Model):
    """
    Modelo para guardar los componentes y su descripción
    """
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Componente")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Modificación")

    class Meta:
        verbose_name = "01 - Componente"
        verbose_name_plural = "01 - Componentes"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Grupo(models.Model):
    """
    Modelo para crear grupos que tengan diferentes componentes y sean reutilizables
    """
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Grupo")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    componentes = models.ManyToManyField(
        Componente, 
        through='EstructuraProyecto',
        verbose_name="Componentes del Grupo",
        help_text="Selecciona los componentes que pertenecen a este grupo"
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Modificación")

    class Meta:
        verbose_name = "02 - Grupo"
        verbose_name_plural = "02 - Grupos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class EstructuraProyecto(models.Model):
    """
    Modelo para definir la estructura de proyectos de componentes en grupos con sus incidencias
    """
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, verbose_name="Grupo")
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE, verbose_name="Componente")
    incidencia = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="% Incidencia",
        help_text="Porcentaje de incidencia del componente en el grupo (0-100%)"
    )
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Orden de Clasificación")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "03 - Estructura Proyecto"
        verbose_name_plural = "03 - Estructuras Proyecto"
        ordering = ['grupo', 'sort_order', 'orden']
        unique_together = ['grupo', 'componente']

    def __str__(self):
        return f"{self.grupo.nombre} - {self.componente.nombre} ({self.incidencia}%)"











