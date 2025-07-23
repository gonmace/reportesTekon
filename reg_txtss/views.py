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
from django.urls import reverse
from django.shortcuts import get_object_or_404


class ListRegistrosView(GenericRegistroTableListView):
    """Vista para listar registros TX/TSS usando tabla genérica."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG
    
    def get_breadcrumbs(self):
        """Genera breadcrumbs para la página de listado."""
        return [
            {'label': 'Inicio', 'url': reverse('dashboard:dashboard')},
            {'label': 'TX/TSS'}  # Página actual sin URL
        ]


class StepsRegistroView(GenericRegistroStepsView):
    """Vista para mostrar los pasos de un registro TX/TSS."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG
    
    def get_context_data(self, **kwargs):
        """Obtiene el contexto y establece el registro, agregando el template de datos clave según el paso actual."""
        registro_id = self.kwargs.get('registro_id')
        self.registro = get_object_or_404(self.registro_config.registro_model, id=registro_id)
        context = super().get_context_data(**kwargs)

        # Determinar el paso actual (puedes ajustar la lógica según tu flujo)
        paso_actual = self.request.GET.get('paso') or 'sitio'
        if paso_actual == 'sitio':
            datos_clave_template = 'components/datos_clave_sitio.html'
        elif paso_actual == 'empalme':
            datos_clave_template = 'components/datos_clave_empalme.html'
        else:
            datos_clave_template = 'components/datos_clave_txtss.html'
        context['datos_clave_template'] = datos_clave_template
        return context
    
    def get_header_title(self):
        """Obtiene el título del header basado en PTI ID o Operador ID."""
        if hasattr(self, 'registro') and self.registro:
            # Intentar obtener PTI ID primero
            pti_id = getattr(getattr(self.registro, 'sitio', None), 'pti_cell_id', None)
            if pti_id:
                return pti_id
            
            # Si no hay PTI ID, intentar Operador ID
            operador_id = getattr(getattr(self.registro, 'sitio', None), 'operator_id', None)
            if operador_id:
                return operador_id
        
        return super().get_header_title()


class ElementoRegistroView(GenericElementoView):
    """Vista para manejar elementos de registro TX/TSS."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG
    
    def get(self, request, registro_id, paso_nombre):
        """Establece el registro antes de procesar la petición."""
        self.registro = self.registro_config.registro_model.objects.get(id=registro_id)
        return super().get(request, registro_id, paso_nombre)
    
    def get_header_title(self):
        """Obtiene el título del header basado en el nombre del sitio."""
        if hasattr(self, 'registro') and self.registro:
            name = getattr(getattr(self.registro, 'sitio', None), 'name', 'Sin PTI')
            return name
        return super().get_header_title()


class ActivarRegistroView(GenericActivarRegistroView):
    """Vista para activar registros TX/TSS."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG 