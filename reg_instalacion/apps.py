"""
Configuración de la aplicación Instalación.
"""

from django.apps import AppConfig


class RegInstalacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reg_instalacion'
    verbose_name = 'Instalación'
    description = 'Aplicación para registros de instalación'
