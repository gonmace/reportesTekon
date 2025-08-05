"""
Vistas para registros Reporte de construcción.
"""

from registros.views.steps_views import (
    GenericRegistroStepsView,
    GenericElementoView,
    GenericRegistroTableListView
)
from registros.views.activation_views import GenericActivarRegistroView
from registros.config import RegistroConfig
from .config import REGISTRO_CONFIG
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.shortcuts import render


class ListRegistrosView(GenericRegistroTableListView):
    """Vista para listar registros Reporte de construcción usando tabla genérica."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG
    
    def get_breadcrumbs(self):
        """Genera breadcrumbs para la página de listado."""
        return [
            {'label': 'Inicio', 'url': reverse('dashboard:dashboard')},
            {'label': 'Reporte de construcción'}  # Página actual sin URL
        ]


class StepsRegistroView(GenericRegistroStepsView):
    """Vista para mostrar los pasos de un registro Reporte de construcción."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG
    
    def get_context_data(self, **kwargs):
        """Obtiene el contexto y establece el registro."""
        registro_id = self.kwargs.get('registro_id')
        self.registro = get_object_or_404(self.registro_config.registro_model, id=registro_id)
        context = super().get_context_data(**kwargs)
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
    
    def get_pdf_url(self, registro_id):
        """Obtiene la URL para generar el PDF."""
        return reverse('reg_construccion:pdf', kwargs={'registro_id': registro_id})


class ElementoRegistroView(GenericElementoView):
    """Vista para manejar elementos de registro Reporte de construcción."""
    
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
    """Vista para activar registros Reporte de construcción."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG


class TableOnlyView(GenericElementoView):
    template_name = 'pages/tabla_avance.html'

    def get_registro_config(self):
        from .config import REGISTRO_CONFIG
        return REGISTRO_CONFIG

    def get(self, request, registro_id, paso_nombre):
        registro = self.registro_config.registro_model.objects.get(id=registro_id)
        paso_config = self.registro_config.pasos.get(paso_nombre)
        elemento_config = paso_config.elemento
        instance = None
        if hasattr(elemento_config, 'model'):
            instance = elemento_config.model.objects.filter(registro=registro).first()
        # Busca el subelemento tipo 'table'
        table_sub = next((s for s in elemento_config.sub_elementos if s.tipo == 'table'), None)
        data = self._get_table_data(registro, table_sub, instance) if table_sub else []
        context = {
            'registro': registro,
            'paso_config': paso_config,
            'elemento_config': elemento_config,
            'breadcrumbs': self.get_breadcrumbs(),
            'header_title': self.get_header_title(),
            'config': table_sub.config if table_sub else {},
            'data': data,
        }
        return render(request, self.template_name, context)