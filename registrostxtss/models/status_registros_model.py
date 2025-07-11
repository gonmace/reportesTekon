from django.db import models
from core.models.sites import Site
from users.models import User
from django.db.models import Q

class RegistrosTxTss(models.Model):
    sitio = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Sitio")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    registro = models.BooleanField(default=False, verbose_name="Registro")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
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
        self.registro0 = True
        self.save()