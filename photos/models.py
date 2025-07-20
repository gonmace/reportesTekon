from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models import BaseModel

class Photos(BaseModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    registro = GenericForeignKey('content_type', 'object_id')
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
    def get_photo_count_and_color(registro_id, etapa):
        """
        Obtiene la cantidad de imágenes para un registro específico y una etapa determinada.
        
        Args:
            registro_id (int): ID del registro
            etapa (str): Nombre de la etapa
            
        Returns:
            int: Cantidad de imágenes encontradas
        """
        
        # Obtener el ContentType del modelo Registros
        from django.contrib.contenttypes.models import ContentType
        from registros_txtss.models import Registros
        
        content_type = ContentType.objects.get_for_model(Registros)
        
        return Photos.objects.filter(
            content_type=content_type,
            object_id=registro_id,
            etapa=etapa
        ).count()


