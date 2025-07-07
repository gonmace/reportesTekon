from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .core_models import BaseModel
from simple_history.models import HistoricalRecords
from users.models import User


class Site(models.Model):
    pti_cell_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="PTI ID", unique=True)
    operator_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Op. ID")
    name = models.CharField(max_length=100, verbose_name="Nombre", unique=True)
    lat_base = models.FloatField(null=True, blank=True, verbose_name="Lat. Base", unique=True)
    lon_base = models.FloatField(null=True, blank=True, verbose_name="Lon. Base", unique=True)
    alt = models.CharField(max_length=100, null=True, blank=True, verbose_name="Alt. (m)")
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name="Region")
    comuna = models.CharField(max_length=100, blank=True, null=True, verbose_name="Comuna")
    is_deleted = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Usuario",
        null=True,
        blank=True,
    )
    history = HistoricalRecords()

    def clean(self):
        """Validación adicional para asegurar que el usuario sea ITO"""
        super().clean()
        if self.user:
            # Si user es un ID (entero), obtener el objeto User
            if isinstance(self.user, int):
                try:
                    user_obj = User.objects.get(id=self.user)
                except User.DoesNotExist:
                    raise ValidationError({'user': 'Usuario no encontrado.'})
            else:
                user_obj = self.user
            
            if user_obj.user_type != User.ITO:
                raise ValidationError({'user': 'Solo se permiten usuarios de tipo ITO para este campo.'})

    def save(self, *args, **kwargs):
        """Valida antes de guardar"""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def tiene_registro_inicial(self):
        """Verifica si el sitio tiene un registro inicial"""
        try:
            from registrosWOM.models import Registros0
            return Registros0.objects.filter(sitio=self).exists()
        except ImportError:
            return False
    
    def get_registro_inicial_id(self):
        """Obtiene el ID del registro inicial si existe"""
        try:
            from registrosWOM.models import Registros0
            registro = Registros0.objects.get(sitio=self)
            return registro.id
        except (ImportError, Registros0.DoesNotExist):
            return None

    class Meta:
        verbose_name = 'Sitio'
        verbose_name_plural = 'Sitios'

    @staticmethod
    def get_table():
        return 'site'

    @staticmethod
    def get_actives():
        return Site.objects.filter(is_deleted=False)
