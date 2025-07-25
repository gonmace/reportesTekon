"""
Configuración de la aplicación Reporte de visita.
"""

from django.apps import AppConfig


class RegVisitaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reg_visita'
    verbose_name = 'Reporte de visita'
    description = 'Aplicación para reporte de visita'
