"""
Vistas simplificadas para registros TX/TSS usando el sistema genérico.
"""

from registros.views.generic_registro_views import (
    GenericRegistroTableListView, 
    GenericRegistroStepsView, 
    GenericElementoView
)
from registros.views.generic_views import GenericActivarRegistroView
from .config import REGISTRO_CONFIG


class ListRegistrosView(GenericRegistroTableListView):
    """Vista para listar registros TX/TSS usando tabla genérica."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG


class StepsRegistroView(GenericRegistroStepsView):
    """Vista para mostrar los pasos de un registro TX/TSS."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG


class ElementoRegistroView(GenericElementoView):
    """Vista para manejar elementos de registro TX/TSS."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG


class ActivarRegistroView(GenericActivarRegistroView):
    """Vista para activar registros TX/TSS."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG 