from django.db import models
from django.utils import timezone
from users.models import User
from core.models.sites import Site
from core.models import BaseModel
from registrostxtss.models.validators import validar_latitud, validar_longitud
from registrostxtss.models.status_registros_model import RegistrosTxTss

class Registros0(BaseModel):
    registro = models.ForeignKey(RegistrosTxTss, on_delete=models.CASCADE, verbose_name='Registro')
    lat = models.FloatField(validators=[validar_latitud], verbose_name='Latitud Inspeccion')
    lon = models.FloatField(validators=[validar_longitud], verbose_name='Longitud Inspeccion')
    altura = models.CharField(max_length=100, verbose_name='Altura Torre')
    dimensiones = models.CharField(max_length=100)
    deslindes = models.CharField(max_length=100)
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro 0'
        verbose_name_plural = 'Registros 0'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.registro} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    @staticmethod
    def get_table():
        return 'registros0'
    
    @staticmethod
    def get_actives():
        return Registros0.objects.filter(is_deleted=False)


class Registros1(BaseModel):
    pass