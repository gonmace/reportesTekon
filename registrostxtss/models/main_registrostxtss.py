from django.db import models
from core.models.sites import Site
from users.models import User
from django.db.models import Q
from core.models.core_models import BaseModel


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


