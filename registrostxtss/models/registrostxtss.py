from django.db import models
from core.models.sites import Site
from users.models import User
from core.models.core_models import BaseModel
from django.utils import timezone

class RegistrosTxTss(BaseModel):
    sitio = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Sitio")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    is_deleted = models.BooleanField(default=False, verbose_name="Registro")
    
    class Meta:
        verbose_name = "Registro Tx/Tss"
        verbose_name_plural = "Registros Tx/Tss"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['sitio', 'user'],
                name='unique_sitio_user_combination'
            )
        ]

    def __str__(self):
        return f"{self.sitio} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    def activar_registro(self):
        self.is_deleted = False
        self.save()

class MapasGoogle(models.Model):
    """
    Modelo para almacenar las imágenes de desfase generadas
    """
    registro = models.ForeignKey(RegistrosTxTss, on_delete=models.CASCADE, related_name='mapas_desfase')
    etapa = models.CharField(max_length=100, verbose_name='Etapa')
    archivo = models.FileField(upload_to='google_maps/')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Mapa Google'
        verbose_name_plural = 'Mapas Google'
    
    def __str__(self):
        return f"{self.registro} - {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def nombre_archivo(self):
        return self.archivo.name.split('/')[-1] if self.archivo else '' 
