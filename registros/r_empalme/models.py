from django.db import models
from core.models import BaseModel
from registros.models.registrostxtss import Registros
from registros.models.completeness_checker import check_model_completeness


class REmpalme(BaseModel):
    registro = models.ForeignKey(Registros, on_delete=models.CASCADE, verbose_name='Registro')
    proveedor = models.CharField(max_length=100, verbose_name='Proveedor')
    capacidad = models.CharField(max_length=100, verbose_name='Capacidad')
    no_poste = models.CharField(max_length=50, verbose_name='No. Poste')
    comentarios = models.TextField(max_length=500, blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Empalme'
        verbose_name_plural = 'Registros Empalme'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.registro} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    @staticmethod
    def get_etapa():
        return 'empalme'
    
    @staticmethod
    def get_actives():
        return REmpalme.objects.filter(is_deleted=False)
    
    @staticmethod
    def check_completeness(rempalme_id):
        return check_model_completeness(REmpalme, rempalme_id) 