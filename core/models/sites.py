from django.db import models
from simple_history.models import HistoricalRecords

class Site(models.Model):
    pti_cell_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="PTI ID", unique=True)
    operator_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Operador ID")
    name = models.CharField(max_length=100, verbose_name="Nombre del sitio", unique=True)
    lat_base = models.FloatField(null=True, blank=True, verbose_name="Latitud Mandato", unique=True)
    lon_base = models.FloatField(null=True, blank=True, verbose_name="Longitud Mandato", unique=True)
    alt = models.IntegerField(null=True, blank=True, verbose_name="Altura (m)")
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name="Región")
    comuna = models.CharField(max_length=100, blank=True, null=True, verbose_name="Comuna")
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def clean(self):
        """Validación adicional para asegurar que el usuario sea ITO"""
        super().clean()
        

    def save(self, *args, **kwargs):
        """Valida antes de guardar"""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pti_cell_id if self.pti_cell_id else '__________'} - {self.operator_id if self.operator_id else '__________'} - {self.name}"


    class Meta:
        verbose_name = 'Sitio'
        verbose_name_plural = 'Sitios'
        ordering = ['pti_cell_id']

    @staticmethod
    def get_table():
        return 'site'

    @staticmethod
    def get_actives():
        return Site.objects.filter(is_deleted=False)
