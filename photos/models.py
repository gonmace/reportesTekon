from django.db import models
from registros.models.registrostxtss import Registros
from core.models import BaseModel

class Photos(BaseModel):
    registro = models.ForeignKey(Registros, on_delete=models.CASCADE)
    etapa = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to='photos/')
    descripcion = models.CharField(max_length=128, blank=True, null=True)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.registro} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
        ordering = ['orden', '-created_at']

    @staticmethod
    def get_photo_count_and_color(sitio_id, etapa):
        """
        Obtiene la cantidad de imágenes para un sitio específico y una etapa determinada.
        
        Args:
            sitio_id (int): ID del sitio
            etapa (str): Nombre de la etapa
            
        Returns:
            int: Cantidad de imágenes encontradas
        """
        
        return Photos.objects.filter(
            registro=sitio_id,
            etapa=etapa
        ).count()


