"""
Configuración de la aplicación Test Completo.
"""

from django.apps import AppConfig


class RegTestCompletoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reg_test_completo'
    verbose_name = 'Test Completo'
    description = 'Aplicación de prueba completa'
