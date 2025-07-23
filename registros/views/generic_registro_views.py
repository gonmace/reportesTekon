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
        
        if getattr(self.registro_config, 'header_title', None):
            context['header_title'] = self.registro_config.header_title
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
    
    def get_header_title(self):
        """Obtiene el título del header. Puede ser sobrescrito."""
        return self.registro_config.header_title or self.registro_config.title
    
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
            'header_title': self.get_header_title(),  # Usar método personalizable
        })
        return context
    
    def _process_map_config(self, registro, elemento_config, instance):
        """
        Procesa la configuración del mapa y obtiene las coordenadas (máximo 3).
        
        Args:
            registro: Instancia del registro principal
            elemento_config: Configuración del elemento
            instance: Instancia del modelo del paso actual
        
        Returns:
            dict: Configuración del mapa con coordenadas procesadas (máximo 3)
        """
        # Buscar configuración del mapa
        map_config = None
        for sub in elemento_config.sub_elementos:
            if sub.tipo == 'mapa':
                map_config = sub.config
                break
        
        if not map_config:
            return {
                'enabled': False,
                'status': 'warning',
                'coordinates': {},
                'etapa': ''
            }
        
        coordinates = {}
        coord_index = 1
        
        # Obtener configuración de iconos del modelo principal
        icon_config = map_config.get('icon_config', {})
        primary_color = icon_config.get('color', '#F59E0B')
        primary_size = icon_config.get('size', 'mid')
        
        # Procesar coordenadas del modelo actual (coord1)
        if instance and hasattr(instance, map_config.get('lat_field', 'lat')):
            lat_field = map_config.get('lat_field', 'lat')
            lon_field = map_config.get('lon_field', 'lon')
            name_field = map_config.get('name_field', 'name')
            
            lat_value = getattr(instance, lat_field, None)
            lon_value = getattr(instance, lon_field, None)
            name_value = getattr(instance, name_field, None) if hasattr(instance, name_field) else 'Inspección'
            
            if lat_value is not None and lon_value is not None:
                coordinates[f'coord{coord_index}'] = {
                    'lat': float(lat_value),
                    'lon': float(lon_value),
                    'label': name_value or 'Inspección',
                    'color': primary_color,
                    'size': primary_size
                }
                coord_index += 1
        
        # Procesar coordenadas del segundo modelo si existe (coord2)
        if 'second_model' in map_config and coord_index <= 3:
            second_model_config = map_config['second_model']
            second_model_class = second_model_config['model_class']
            lat_field = second_model_config['lat_field']
            lon_field = second_model_config['lon_field']
            name_field = second_model_config['name_field']
            relation_field = second_model_config['relation_field']
            
            # Obtener configuración de iconos del segundo modelo
            second_icon_config = second_model_config.get('icon_config', {})
            second_color = second_icon_config.get('color', '#3B82F6')
            second_size = second_icon_config.get('size', 'normal')
            
            # Obtener la instancia del segundo modelo
            second_instance = None
            if relation_field == 'sitio':
                # Para el modelo Site, usar la relación directa
                second_instance = getattr(registro, 'sitio', None)
            else:
                # Para otros modelos, buscar por relación con el registro
                try:
                    second_instance = second_model_class.objects.filter(
                        **{relation_field: registro}
                    ).first()
                except Exception:
                    pass
            
            if second_instance and hasattr(second_instance, lat_field):
                lat_value = getattr(second_instance, lat_field, None)
                lon_value = getattr(second_instance, lon_field, None)
                name_value = getattr(second_instance, name_field, None) if hasattr(second_instance, name_field) else 'Mandato'
                
                if lat_value is not None and lon_value is not None:
                    coordinates[f'coord{coord_index}'] = {
                        'lat': float(lat_value),
                        'lon': float(lon_value),
                        'label': name_value or 'Mandato',
                        'color': second_color,
                        'size': second_size
                    }
                    coord_index += 1
        
        # Procesar coordenadas adicionales si existen (coord3) - para futuras expansiones
        # Por ahora, solo soportamos 2 coordenadas máximo
        
        # Determinar el estado del mapa
        map_status = 'success' if coordinates else 'warning'
        
        return {
            'enabled': True,
            'status': map_status,
            'coordinates': coordinates,
            'etapa': elemento_config.nombre
        }

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
            
            # Obtener configuración de fotos si existe
            photo_config = None
            min_count = 0
            if has_photos:
                for sub in elemento_config.sub_elementos:
                    if sub.tipo == 'fotos':
                        photo_config = sub.config
                        min_count = photo_config.get('min_files', 4)
                        break
            
            # Contar fotos si el paso las tiene
            photo_count = 0
            if has_photos:
                from photos.models import Photos
                from django.contrib.contenttypes.models import ContentType
                
                # Obtener el ContentType del modelo del registro
                content_type = ContentType.objects.get_for_model(type(registro))
                
                # Determinar el nombre de la app para el filtro
                app_filter = self.registro_config.app_namespace
                
                # Contar fotos para este registro, etapa y app
                photo_count = Photos.count_photos(
                    registro_id=registro.id,
                    etapa=step_name,
                    app_name=app_filter,
                    content_type=content_type
                )
            
            # Procesar configuración del mapa
            map_config = self._process_map_config(registro, elemento_config, instance)
            
            # Verificar completitud
            completeness = elemento.get_completeness_info() if hasattr(elemento, 'get_completeness_info') else None
            if completeness is None:
                completeness = {
                    'color': 'gray',
                    'is_complete': False,
                    'missing_fields': [],
                    'total_fields': 0,
                    'filled_fields': 0
                }

            # --- Lógica de color para el botón del formulario ---
            if completeness['total_fields'] == 0:
                form_color = 'error'

            elif completeness['filled_fields'] < completeness['total_fields']:
                form_color = 'warning'
            else:
                form_color = 'success'

            # Generar estructura que espera el template step_generic.html
            step_data = {
                'title': paso_config.title,
                'step_name': step_name,
                'registro_id': registro.id,
                'elements': {
                    'form': {
                        'url': f'/{self.registro_config.app_namespace}/{registro.id}/{step_name}/',
                        'color': form_color
                    },
                    'photos': {
                        'enabled': has_photos,
                        'url': f'/{self.registro_config.app_namespace}/{registro.id}/{step_name}/photos/' if has_photos else '',
                        'color': 'success' if has_photos and photo_count >= min_count else 'warning' if has_photos and photo_count > 0 else 'error',
                        'count': photo_count,
                        'required': has_photos,
                        'min_count': min_count
                    },
                    'map': map_config,
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
    
    def get_header_title(self):
        """Obtiene el título del header. Puede ser sobrescrito."""
        return self.registro_config.header_title or self.registro_config.title
    
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
                'header_title': self.get_header_title(),
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
                        'header_title': self.get_header_title(),
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