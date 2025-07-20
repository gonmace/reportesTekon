"""
Vistas para registros TX/TSS.
"""

from registros.views.base import RegistroListView, RegistroStepsView, ElementoView
from registros.views.generic_views import GenericRegistroView
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Registros
from .elementos import ElementoSitio, ElementoAcceso, ElementoEmpalme
from registros.forms.activar import ActivarRegistroForm
from typing import Dict, Any


class ListRegistrosView(RegistroListView):
    """Vista para listar registros TX/TSS."""
    model = Registros
    template_name = 'pages/main_txtss.html'
    
    class Meta:
        title = 'Registros TX/TSS'
        header_title = 'Registros TX/TSS'
        breadcrumbs = [
            {'label': 'Inicio', 'url_name': 'dashboard:dashboard'},
            {'label': 'TX/TSS'}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ActivarRegistroForm()
        return context


class ActivarRegistroView(LoginRequiredMixin, FormView):
    """Vista para activar registros TX/TSS."""
    template_name = 'pages/main_txtss.html'
    form_class = ActivarRegistroForm
    
    def form_valid(self, form):
        try:
            registro = form.save()
            messages.success(self.request, f'Registro activado exitosamente para {registro.sitio.name}')
            
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Registro activado exitosamente para {registro.sitio.name}'
                })
            else:
                return redirect('registros_txtss:list')
        except Exception as e:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=400)
            else:
                messages.error(self.request, f'Error al activar registro: {str(e)}')
                return self.form_invalid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Error en el formulario',
                'errors': form.errors
            }, status=400)
        else:
            return super().form_invalid(form)


class StepsRegistroView(RegistroStepsView):
    """Vista para mostrar los pasos de un registro TX/TSS."""
    model = Registros
    template_name = 'pages/steps_txtss.html'
    
    def get_steps_config(self) -> Dict[str, Dict[str, Any]]:
        """Configuración de los pasos."""
        return {
            'sitio': {
                'elemento_class': ElementoSitio,
                'title': 'Sitio',
                'description': 'Información general del sitio.',
            },
            'acceso': {
                'elemento_class': ElementoAcceso,
                'title': 'Acceso',
                'description': 'Información sobre el acceso al sitio.',
            },
            'empalme': {
                'elemento_class': ElementoEmpalme,
                'title': 'Empalme',
                'description': 'Información sobre el empalme.',
            },
        }


class ElementoRegistroView(ElementoView):
    """Vista para manejar elementos de registro TX/TSS."""
    model = Registros
    
    def get_elemento_class(self, paso_nombre):
        """Obtiene la clase del elemento basada en el paso."""
        elementos_map = {
            'sitio': ElementoSitio,
            'acceso': ElementoAcceso,
            'empalme': ElementoEmpalme,
        }
        return elementos_map.get(paso_nombre)
