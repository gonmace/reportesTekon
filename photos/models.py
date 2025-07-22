from django.db import models
from core.models import BaseModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Photos(BaseModel):
    # Referencia genérica al modelo de Registro (puede ser de cualquier app)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    registro = GenericForeignKey('content_type', 'object_id')
    
    # Campo para identificar la aplicación
    app = models.CharField(max_length=100, verbose_name='Aplicación')
    etapa = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to='photos/')
    descripcion = models.CharField(max_length=128, blank=True, null=True)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.registro} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = 'Foto'
        verbose_name_plural = 'Fotos'
        ordering = ['orden', '-created_at']

    @staticmethod
    def count_photos(registro_id, etapa, app_name=None, content_type=None):
        """
        Cuenta las fotos para un registro específico, etapa y aplicación.
        
        Args:
            registro_id (int): ID del registro
            etapa (str): Nombre de la etapa
            app_name (str, optional): Nombre de la aplicación
            content_type (ContentType, optional): ContentType del modelo
            
        Returns:
            int: Cantidad de fotos encontradas
        """
        filters = {
            'object_id': registro_id,
            'etapa': etapa,
        }
        
        # Usar content_type si está disponible
        if content_type:
            filters['content_type'] = content_type
        
        # Usar app_name si está disponible (puede usarse junto con content_type)
        if app_name:
            filters['app'] = app_name
            
        return Photos.objects.filter(**filters).count()

    @staticmethod
    def get_photo_count_and_color(registro_id, etapa, app_name=None, content_type=None):
        """
        Obtiene la cantidad de imágenes para un registro específico y una etapa determinada.
        
        Args:
            registro_id (int): ID del registro
            etapa (str): Nombre de la etapa
            app_name (str, optional): Nombre de la aplicación
            content_type (ContentType, optional): ContentType del modelo
            
        Returns:
            int: Cantidad de imágenes encontradas
        """
        return Photos.count_photos(registro_id, etapa, app_name, content_type)


