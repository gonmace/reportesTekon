"""
Configuración de la aplicación Mantenimiento Preventivo.
"""

from django.apps import AppConfig


class RegMantenimientoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reg_mantenimiento'
    verbose_name = 'Mantenimiento Preventivo'
    description = 'Aplicación para registros de mantenimiento preventivo de equipos'
