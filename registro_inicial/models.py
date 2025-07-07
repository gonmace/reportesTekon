from django.db import models
from django.contrib.auth.models import User
from core.models.sites import Site


class RegistroInicial(models.Model):
    sitio = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Sitio")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    fecha = models.DateField(verbose_name="Fecha")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Registro Inicial"
        verbose_name_plural = "Registros Iniciales"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - {self.fecha}"
