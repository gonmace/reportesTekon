"""
Vistas genéricas para registros basadas en configuración declarativa.
"""

from django.views.generic import TemplateView, ListView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django_tables2 import SingleTableView
from core.utils.breadcrumbs import BreadcrumbsMixin
from registros.mixins.breadcrumbs_mixin import RegistroBreadcrumbsMixin
from registros.components.registro_config import RegistroConfig, ElementoGenerico
from registros.forms.activar import create_activar_registro_form
from registros.tables import create_registros_table
from typing import Dict, Any


class GenericRegistroListView(LoginRequiredMixin, BreadcrumbsMixin, ListView):
    """
    Vista genérica para listar registros basada en configuración.
    """
    context_object_name = 'registros'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registro_config = self.get_registro_config()
        # Usar template de la configuración
        self.template_name = self.registro_config.list_template
    
    def get_registro_config(self) -> RegistroConfig:
        """Obtiene la configuración del registro. Debe ser sobrescrito."""
        raise NotImplementedError("Debe implementar get_registro_config()")
    
    def get_queryset(self):
        """Obtiene los registros activos."""
        return self.registro_config.registro_model.objects.filter(
            is_active=True, 
            is_deleted=False
        )
    
    def get_context_data(self, **kwargs):
        """Obtiene el contexto con estadísticas."""
        context = super().get_context_data(**kwargs)
        context.update({
            'total_registros': self.get_queryset().count(),
            'form': create_activar_registro_form(
                registro_model=self.registro_config.registro_model,
                title_default=self.registro_config.title,
                description_default=f'Registro {self.registro_config.title} activado desde el formulario'
            )(),
            'title': self.registro_config.title,
            'breadcrumbs': self.registro_config.breadcrumbs,
        })
        return context


class GenericRegistroTableListView(LoginRequiredMixin, BreadcrumbsMixin, SingleTableView):
    """
    Vista genérica para listar registros usando django-tables2.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registro_config = self.get_registro_config()
        self.template_name = self.registro_config.list_template
        # Crear tabla dinámicamente
        self.table_class = create_registros_table(
            self.registro_config.registro_model,
            self.registro_config.app_namespace
        )
    
    def get_registro_config(self) -> RegistroConfig:
        """Obtiene la configuración del registro. Debe ser sobrescrito."""
        raise NotImplementedError("Debe implementar get_registro_config()")
    
    def get_queryset(self):
        """Filtrar registros según el usuario y sus permisos."""
        queryset = self.registro_config.registro_model.objects.filter(is_deleted=False)
        
        # Si el usuario es superusuario, mostrar todos los registros activos
        if self.request.user.is_superuser:
            return queryset
        
        # Para usuarios normales, mostrar solo sus registros activos
        return queryset.filter(user=self.request.user)
    
    def get_table(self, **kwargs):
        """Pasar el usuario a la tabla para configurar columnas."""
        table = super().get_table(**kwargs)
        table.user = self.request.user
        table.app_namespace = self.registro_config.app_namespace
        return table
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Configuración específica
        context.update({
            'page_title': self.registro_config.title,
            'show_activate_button': True,
            'activate_button_text': 'Activar Registro',
            'activar_url': self.request.build_absolute_uri(f'/{self.registro_config.app_namespace}/activar/'),
            'modal_template': 'components/activar_registro_form.html',
            'form': create_activar_registro_form(
                registro_model=self.registro_config.registro_model,
                title_default=self.registro_config.title,
                description_default=f'Registro {self.registro_config.title} activado desde el formulario'
            )(),
        })
        
        return context


class GenericRegistroStepsView(RegistroBreadcrumbsMixin, LoginRequiredMixin, BreadcrumbsMixin, TemplateView):
    """
    Vista genérica para mostrar los pasos de un registro.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registro_config = self.get_registro_config()
        # Usar template de la configuración
        self.template_name = self.registro_config.steps_template
    
    def get_registro_config(self) -> RegistroConfig:
        """Obtiene la configuración del registro. Debe ser sobrescrito."""
        raise NotImplementedError("Debe implementar get_registro_config()")
    
    def get_context_data(self, **kwargs):
        """Obtiene el contexto con los pasos configurados."""
        context = super().get_context_data(**kwargs)
        
        registro_id = self.kwargs.get('registro_id')
        registro = get_object_or_404(self.registro_config.registro_model, id=registro_id)
        
        # Generar contexto de pasos
        steps_context = self._generate_steps_context(registro)
        
        context.update({
            'registro': registro,
            'steps': steps_context,
            'steps_config': self.registro_config.pasos,
            'title': self.registro_config.title,
            'registro_title': registro.title,  # Agregar título del registro
            'breadcrumbs': self.get_breadcrumbs(),  # Usar breadcrumbs dinámicos
        })
        return context
    
    def _generate_steps_context(self, registro):
        """Genera el contexto para cada paso."""
        steps_context = []
        
        for step_name, paso_config in self.registro_config.pasos.items():
            elemento_config = paso_config.elemento
            elemento = ElementoGenerico(registro, elemento_config)
            instance = elemento.get_or_create()
            if instance:
                elemento = ElementoGenerico(registro, elemento_config, instance)
            
            # Verificar sub-elementos
            has_photos = any(sub.tipo == 'fotos' for sub in elemento_config.sub_elementos)
            has_map = any(sub.tipo == 'mapa' for sub in elemento_config.sub_elementos)
            
            # Verificar completitud
            completeness = elemento.check_completeness() if hasattr(elemento, 'check_completeness') else {
                'color': 'gray',
                'is_complete': False,
                'missing_fields': [],
                'total_fields': 0,
                'filled_fields': 0
            }
            
            # Generar estructura que espera el template step_generic.html
            step_data = {
                'title': paso_config.title,
                'step_name': step_name,
                'registro_id': registro.id,
                'elements': {
                    'form': {
                        'url': f'/txtss/{registro.id}/{step_name}/',
                        'color': 'success' if instance else 'warning'
                    },
                    'photos': {
                        'enabled': has_photos,
                        'url': f'/txtss/{registro.id}/{step_name}/fotos/' if has_photos else '',
                        'color': 'success' if has_photos and instance else 'warning',
                        'count': 0,  # TODO: Implementar conteo de fotos
                        'required': has_photos,
                        'min_count': 1 if has_photos else 0
                    },
                    'map': {
                        'enabled': has_map,
                        'status': 'success' if has_map and instance else 'warning',
                        'coordinates': {},  # TODO: Implementar coordenadas
                        'etapa': step_name
                    },
                    'desfase': {
                        'enabled': False,  # TODO: Implementar si es necesario
                        'distancia': None,
                        'description': '',
                        'color': 'gray'
                    }
                },
                'completeness': completeness,
                'instance': instance,
                'elemento': elemento
            }
            
            # Return as tuple (step_name, step_data) to match template expectation
            steps_context.append((step_name, step_data))
        
        return steps_context


class GenericElementoView(RegistroBreadcrumbsMixin, LoginRequiredMixin, BreadcrumbsMixin, View):
    """
    Vista genérica para manejar elementos de registro.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registro_config = self.get_registro_config()
    
    def get_registro_config(self) -> RegistroConfig:
        """Obtiene la configuración del registro. Debe ser sobrescrito."""
        raise NotImplementedError("Debe implementar get_registro_config()")
    
    def get(self, request, registro_id, paso_nombre):
        """Maneja las peticiones GET."""
        try:
            registro = get_object_or_404(self.registro_config.registro_model, id=registro_id)
            paso_config = self.registro_config.pasos.get(paso_nombre)
            
            if not paso_config:
                messages.error(request, f'Paso "{paso_nombre}" no encontrado')
                return redirect(f'{self.registro_config.app_namespace}:steps', registro_id=registro_id)
            
            elemento_config = paso_config.elemento
            elemento = ElementoGenerico(registro, elemento_config)
            instance = elemento.get_or_create()
            
            if instance:
                elemento = ElementoGenerico(registro, elemento_config, instance)
            
            form = elemento.get_form()
            
            context = {
                'registro': registro,
                'paso_config': paso_config,
                'elemento_config': elemento_config,
                'elemento': elemento,
                'form': form,
                'instance': instance,
                'title': self.registro_config.title,
                'breadcrumbs': self.get_breadcrumbs(),
            }
            
            return render(request, elemento_config.template_name, context)
            
        except Exception as e:
            messages.error(request, f'Error al cargar el elemento: {str(e)}')
            return redirect(f'{self.registro_config.app_namespace}:steps', registro_id=registro_id)
    
    def post(self, request, registro_id, paso_nombre):
        """Maneja las peticiones POST."""
        try:
            registro = get_object_or_404(self.registro_config.registro_model, id=registro_id)
            paso_config = self.registro_config.pasos.get(paso_nombre)
            
            if not paso_config:
                messages.error(request, f'Paso "{paso_nombre}" no encontrado')
                return redirect(f'{self.registro_config.app_namespace}:steps', registro_id=registro_id)
            
            elemento_config = paso_config.elemento
            elemento = ElementoGenerico(registro, elemento_config)
            instance = elemento.get_or_create()
            
            if instance:
                elemento = ElementoGenerico(registro, elemento_config, instance)
            
            form = elemento.get_form(request.POST, request.FILES)
            
            if form.is_valid():
                elemento.save(form)
                messages.success(request, elemento_config.success_message)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': elemento_config.success_message
                    })
                else:
                    return redirect(f'{self.registro_config.app_namespace}:steps', registro_id=registro_id)
            else:
                messages.error(request, elemento_config.error_message)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': elemento_config.error_message,
                        'errors': form.errors
                    }, status=400)
                else:
                    context = {
                        'registro': registro,
                        'paso_config': paso_config,
                        'elemento_config': elemento_config,
                        'elemento': elemento,
                        'form': form,
                        'instance': instance,
                        'title': self.registro_config.title,
                        'breadcrumbs': self.get_breadcrumbs(),
                    }
                    return render(request, elemento_config.template_name, context)
                    
        except Exception as e:
            error_message = f'Error al guardar el elemento: {str(e)}'
            messages.error(request, error_message)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=400)
            else:
                return redirect(f'{self.registro_config.app_namespace}:steps', registro_id=registro_id)
    
    def render_response(self, request, context):
        """Renderiza la respuesta."""
        return render(request, context['elemento_config'].template_name, context) 