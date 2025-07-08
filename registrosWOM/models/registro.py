from django.db import models
from core.models.sites import Site


class Registros(models.Model):
    sitio = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Sitio")
    registro0 = models.BooleanField(default=False, verbose_name="Registro 0")
    registro1 = models.BooleanField(default=False, verbose_name="Registro 1")
    registro2 = models.BooleanField(default=False, verbose_name="Registro 2")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Registro WOM"
        verbose_name_plural = "Registros WOM"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sitio} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
