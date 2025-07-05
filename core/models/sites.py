from django.db import models
from django.contrib.auth import get_user_model

from .core_models import BaseModel
from simple_history.models import HistoricalRecords

User = get_user_model()

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
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sitio'
        verbose_name_plural = 'Sitios'

    @staticmethod
    def get_table():
        return 'site'

    @staticmethod
    def get_actives():
        return Site.objects.filter(is_deleted=False)
