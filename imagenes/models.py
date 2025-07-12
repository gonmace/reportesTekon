from django.db import models
from core.models.registros import Registro
from core.models import BaseModel

class Imagenes(BaseModel):
    registro = models.ForeignKey(Registro, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='imagenes/')
    descripcion = models.TextField(blank=True, null=True)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.registro} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = 'Imagen'
        verbose_name_plural = 'Imagenes'
        ordering = ['orden', '-created_at']

