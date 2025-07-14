from django.db import models
from registrostxtss.models.main_registrostxtss import RegistrosTxTss
from core.models import BaseModel

class Photos(BaseModel):
    registro = models.ForeignKey(RegistrosTxTss, on_delete=models.CASCADE)
    etapa = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to='photos/')
    descripcion = models.TextField(blank=True, null=True)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.registro} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
        ordering = ['orden', '-created_at']

