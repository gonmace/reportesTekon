from django.db import models
from core.models.sites import Site


class Registros0(models.Model):
    sitio = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Sitio")
    fecha = models.DateField(verbose_name="Fecha")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Registro WOM"
        verbose_name_plural = "Registros WOM"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sitio} - {self.fecha}"
