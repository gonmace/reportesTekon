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
from registros.components.editable_table import EditableTableElemento
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
            pass  # No filtrar por usuario
        else:
            # Para usuarios normales, mostrar solo sus registros activos
            queryset = queryset.filter(user=self.request.user)
        
        # Si permite múltiples registros por sitio, mostrar solo el más reciente por sitio
        if getattr(self.registro_config, 'allow_multiple_per_site', False):
            from django.db.models import Max
            # Obtener los IDs de los registros más recientes por sitio
            latest_registros = queryset.values('sitio').annotate(
                latest_fecha=Max('fecha')
            ).values_list('sitio', 'latest_fecha')
            
            # Filtrar para obtener solo los registros más recientes
            filtered_queryset = self.registro_config.registro_model.objects.none()
            for sitio_id, latest_fecha in latest_registros:
                latest_registro = queryset.filter(
                    sitio_id=sitio_id,
                    fecha=latest_fecha
                ).first()
                if latest_registro:
                    filtered_queryset = filtered_queryset | self.registro_config.registro_model.objects.filter(id=latest_registro.id)
            
            return filtered_queryset
        
        return queryset
    
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
            'app_namespace': self.registro_config.app_namespace,  # Agregar namespace para URLs
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
    
    def get_pdf_url(self, registro_id):
        """Obtiene la URL para generar el PDF. Debe ser sobrescrito."""
        return None
    
    def get_context_data(self, **kwargs):
        """Obtiene el contexto con los pasos configurados."""
        context = super().get_context_data(**kwargs)
        
        registro_id = self.kwargs.get('registro_id')
        registro = get_object_or_404(self.registro_config.registro_model, id=registro_id)
        
        # Obtener registros del mismo sitio para el selector de fecha
        registros_sitio = self.registro_config.registro_model.objects.filter(
            sitio=registro.sitio,
            user=registro.user
        ).order_by('-fecha')
        
        # Generar contexto de pasos
        steps_context = self._generate_steps_context(registro)
        
        # Generar URL del PDF
        pdf_url = self.get_pdf_url(registro_id)
        
        context.update({
            'registro': registro,
            'registros_sitio': registros_sitio,  # Agregar registros del mismo sitio
            'steps': steps_context,
            'steps_config': self.registro_config.pasos,
            'title': self.registro_config.title,
            'registro_title': registro.title,  # Agregar título del registro
            'breadcrumbs': self.get_breadcrumbs(),  # Usar breadcrumbs dinámicos
            'header_title': self.get_header_title(),  # Usar método personalizable
            'app_namespace': self.registro_config.app_namespace,  # Agregar namespace para URLs
            'form': create_activar_registro_form(
                registro_model=self.registro_config.registro_model,
                title_default=self.registro_config.title,
                description_default=f'Registro {self.registro_config.title} activado desde el formulario'
            )(),
            'activar_url': f'/{self.registro_config.app_namespace}/activar/',
            'pdf_url': pdf_url,  # Agregar URL del PDF
            'allow_multiple_per_site': getattr(self.registro_config, 'allow_multiple_per_site', False),  # Agregar configuración de múltiples registros
        })
        return context
    
    def _process_map_config(self, registro, elemento_config, instance):
        """
        Procesa la configuración del mapa y obtiene las coordenadas.
        
        Args:
            registro: Instancia del registro principal
            elemento_config: Configuración del elemento
            instance: Instancia del modelo del paso actual
        
        Returns:
            dict: Configuración del mapa con coordenadas procesadas
        """
        # Buscar configuración del mapa
        map_config = self._get_map_config(elemento_config)
        if not map_config:
            return self._get_disabled_map_config()
        
        # Obtener coordenadas
        coordinates = self._get_coordinates(registro, map_config, instance)
        
        # Determinar estado del mapa
        map_status = self._determine_map_status(map_config, coordinates, registro, elemento_config)
        
        # Para mapas de 2 y 3 puntos, siempre mantener habilitado pero cambiar el estado
        required_coords = self._get_required_coords(map_config)
        has_required_coords = len(coordinates) >= required_coords
        
        # Si es mapa de 2 o 3 puntos, siempre mantener enabled=True
        map_type = map_config.get('type', 'single_point')
        if map_type in ['two_point', 'three_point']:
            enabled = True
        else:
            enabled = has_required_coords
        
        result = {
            'enabled': enabled,
            'status': map_status,
            'coordinates': coordinates,
            'etapa': elemento_config.nombre
        }
        # Calcular distancia si corresponde
        if map_config.get('calcular_distancia') and len(coordinates) >= 2:
            try:
                from core.utils.coordenadas import calcular_distancia_geopy
                c1 = coordinates.get('coord1')
                c2 = coordinates.get('coord2')
                if c1 and c2:
                    distancia = calcular_distancia_geopy(c1['lat'], c1['lon'], c2['lat'], c2['lon'])
                    result['distancia'] = int(distancia)
            except Exception as e:
                result['distancia'] = None
        return result
    
    def _get_map_config(self, elemento_config):
        """Obtiene la configuración del mapa desde los sub-elementos."""
        for sub in elemento_config.sub_elementos:
            if sub.tipo == 'mapa':
                return sub.config
        return None
    
    def _get_disabled_map_config(self):
        """Retorna configuración para mapa deshabilitado."""
        return {
            'enabled': False,
            'status': 'warning',
            'coordinates': {},
            'etapa': ''
        }
    
    def _get_coordinates(self, registro, map_config, instance):
        """Obtiene todas las coordenadas del mapa."""
        coordinates = {}
        coord_index = 1
        
        # Coordenada 1: modelo actual o sitio
        coord1 = self._get_coordinate_1(map_config, instance, registro)
        if coord1:
            coordinates[f'coord{coord_index}'] = coord1
            coord_index += 1
        
        # Coordenada 2: segundo modelo
        if 'second_model' in map_config:
            coord2 = self._get_coordinate_2(map_config, registro)
            if coord2:
                coordinates[f'coord{coord_index}'] = coord2
                coord_index += 1
        
        # Coordenada 3: tercer modelo
        if 'third_model' in map_config:
            coord3 = self._get_coordinate_3(map_config, registro)
            if coord3:
                coordinates[f'coord{coord_index}'] = coord3
        
        return coordinates
    
    def _get_coordinate_1(self, map_config, instance, registro):
        """Obtiene la primera coordenada (modelo actual o sitio)."""
        name1 = map_config.get('name_field', 'Inspección')
        if instance and hasattr(instance, map_config.get('lat_field', 'lat')):
            # Modelo del paso actual
            return self._extract_coordinate(
                instance, 
                map_config.get('lat_field', 'lat'),
                map_config.get('lon_field', 'lon'),
                map_config.get('name_field', 'name'),
                name1,
                map_config.get('icon_config', {})
            )
        elif not instance and map_config.get('type') == 'single_point':
            # Modelo Site (mandato)
            if hasattr(registro, 'sitio') and registro.sitio:
                return self._extract_coordinate(
                    registro.sitio,
                    map_config.get('lat_field', 'lat_base'),
                    map_config.get('lon_field', 'lon_base'),
                    map_config.get('name_field', 'name'),
                    name1,
                    map_config.get('icon_config', {})
                )
        return None

    def _get_coordinate_2(self, map_config, registro):
        """Obtiene la segunda coordenada."""
        second_config = map_config['second_model']
        name2 = second_config.get('name_field', 'Mandato')
        second_instance = self._get_related_instance(
            registro, 
            second_config['model_class'], 
            second_config['relation_field']
        )
        
        if second_instance:
            return self._extract_coordinate(
                second_instance,
                second_config['lat_field'],
                second_config['lon_field'],
                second_config['name_field'],
                name2,
                second_config.get('icon_config', {})
            )
        return None

    def _get_coordinate_3(self, map_config, registro):
        """Obtiene la tercera coordenada."""
        third_config = map_config['third_model']
        name3 = third_config.get('name_field', 'Punto 3')
        third_instance = self._get_related_instance(
            registro,
            third_config['model_class'],
            third_config['relation_field']
        )
        
        if third_instance:
            return self._extract_coordinate(
                third_instance,
                third_config['lat_field'],
                third_config['lon_field'],
                third_config['name_field'],
                name3,
                third_config.get('icon_config', {})
            )
        return None
    
    def _get_related_instance(self, registro, model_class, relation_field):
        """Obtiene la instancia relacionada."""
        if relation_field == 'sitio':
            return getattr(registro, 'sitio', None)
        
        try:
            return model_class.objects.filter(**{relation_field: registro}).first()
        except Exception:
            return None
    
    def _extract_coordinate(self, instance, lat_field, lon_field, name_field, default_name, icon_config):
        """Extrae coordenadas de una instancia."""
        if not hasattr(instance, lat_field):
            return None
        
        lat_value = getattr(instance, lat_field, None)
        lon_value = getattr(instance, lon_field, None)
        name_value = getattr(instance, name_field, None) if hasattr(instance, name_field) else default_name
        
        if lat_value is not None and lon_value is not None:
            return {
                'lat': float(lat_value),
                'lon': float(lon_value),
                'label': name_value or default_name,
                'color': icon_config.get('color', '#F59E0B'),
                'size': icon_config.get('size', 'mid')
            }
        return None
    
    def _get_required_coords(self, map_config):
        """Determina cuántas coordenadas son requeridas."""
        map_type = map_config.get('type', 'single_point')
        
        if map_type == 'single_point':
            return 1
        elif map_type == 'two_point' and 'second_model' in map_config:
            return 2
        elif map_type == 'three_point':
            return 3
        
        return 1
    
    def _determine_map_status(self, map_config, coordinates, registro, elemento_config):
        """Determina el estado del mapa."""
        required_coords = self._get_required_coords(map_config)
        has_required_coords = len(coordinates) >= required_coords
        
        map_type = map_config.get('type', 'single_point')
        
        # Para mapas de 2 y 3 puntos sin coordenadas completas, usar 'disabled'
        if map_type in ['two_point', 'three_point'] and not has_required_coords:
            return 'disabled'
        
        if not has_required_coords:
            return 'warning'
        
        # Verificar si existe imagen guardada
        has_saved_image = self._check_saved_image(registro, elemento_config)
        
        if map_type == 'single_point':
            return 'error' if not has_saved_image else 'success'
        elif map_type == 'two_point':
            return 'error' if not has_saved_image else 'success'
        elif map_type == 'three_point':
            # Para mapas de 3 puntos: error si no tiene imagen guardada, success si la tiene
            return 'error' if not has_saved_image else 'success'
        else:
            return 'success'
    
    def _check_saved_image(self, registro, elemento_config):
        """Verifica si existe una imagen guardada del mapa."""
        try:
            from core.models.google_maps import GoogleMapsImage
            from django.contrib.contenttypes.models import ContentType
            
            content_type = ContentType.objects.get_for_model(type(registro))
            return GoogleMapsImage.objects.filter(
                content_type=content_type,
                object_id=registro.id,
                etapa=elemento_config.nombre
            ).exists()
        except Exception:
            return False

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
            
            # Buscar el template de datos clave del subelemento de tipo mapa
            datos_clave_template = None
            for sub in getattr(elemento_config, 'sub_elementos', []):
                if getattr(sub, 'tipo', None) == 'mapa' and getattr(sub, 'template_datos_clave', None):
                    datos_clave_template = sub.template_datos_clave
                    break
            
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
            elif completeness['filled_fields'] == 0:
                form_color = 'error'  # Sin campos llenos = rojo
            elif completeness['filled_fields'] < completeness['total_fields']:
                form_color = 'warning'  # Algunos campos llenos = amarillo
            else:
                form_color = 'success'  # Todos los campos llenos = verde

            # Verificar si es un paso solo con componentes (sin formulario)
            is_component_only = elemento_config.model is None and elemento_config.form_class is None
            
            # Verificar si es una tabla editable
            is_table = (elemento_config.template_name == 'components/editable_table.html' or 
                       any(sub.tipo == 'editable_table' for sub in elemento_config.sub_elementos))
            
            # Generar estructura que espera el template step_item.html
            step_data = {
                'title': paso_config.title,
                'step_name': step_name,
                'registro_id': registro.id,
                'is_table': is_table,  # Agregar propiedad para identificar tablas
                'elements': {
                    'form': None if is_component_only else {
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
                    'map': map_config
                },
                'completeness': completeness,
                'instance': instance,
                'elemento': elemento,
                'datos_clave_template': datos_clave_template
            }
            
            # Return as tuple (step_name, step_data) to match template expectation
            steps_context.append((step_name, step_data))
        
        return steps_context


class GenericElementoView(RegistroBreadcrumbsMixin, LoginRequiredMixin, BreadcrumbsMixin, View):
    """
    Vista genérica para manejar elementos de registro (formularios, tablas editables, etc.).
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
        """Maneja peticiones GET."""
        try:
            registro = get_object_or_404(self.registro_config.registro_model, id=registro_id)
            paso_config = self.registro_config.pasos.get(paso_nombre)
            
            if not paso_config:
                return JsonResponse({'error': f'Paso no válido: {paso_nombre}'}, status=400)
            
            elemento_config = paso_config.elemento
            
            # Verificar si es una tabla editable
            if elemento_config.template_name == 'components/editable_table.html' or \
               any(sub.tipo == 'editable_table' for sub in elemento_config.sub_elementos):
                return self.handle_editable_table(request, registro, paso_config, elemento_config)
            
            # Manejo tradicional de formularios
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
            messages.error(request, f"Error al cargar el paso: {str(e)}")
            return redirect(f'{self.registro_config.app_namespace}:steps', registro_id=registro_id)
    
    def post(self, request, registro_id, paso_nombre):
        """Maneja peticiones POST."""
        try:
            registro = get_object_or_404(self.registro_config.registro_model, id=registro_id)
            paso_config = self.registro_config.pasos.get(paso_nombre)
            
            if not paso_config:
                return JsonResponse({'error': f'Paso no válido: {paso_nombre}'}, status=400)
            
            elemento_config = paso_config.elemento
            
            # Verificar si es una tabla editable
            if elemento_config.template_name == 'components/editable_table.html' or \
               any(sub.tipo == 'editable_table' for sub in elemento_config.sub_elementos):
                return self.handle_editable_table_post(request, registro, paso_config, elemento_config)
            
            # Manejo tradicional de formularios
            elemento = ElementoGenerico(registro, elemento_config)
            instance = elemento.get_or_create()
            if instance:
                elemento = ElementoGenerico(registro, elemento_config, instance)
            
            form = elemento.get_form(data=request.POST, files=request.FILES)
            
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
            messages.error(request, f"Error al procesar el paso: {str(e)}")
            return redirect(f'{self.registro_config.app_namespace}:steps', registro_id=registro_id)
    
    def handle_editable_table(self, request, registro, paso_config, elemento_config):
        """Maneja la visualización de tablas editables."""
        # Buscar configuración de tabla editable en sub_elementos
        table_config = None
        for sub_elemento in elemento_config.sub_elementos:
            if sub_elemento.tipo == 'editable_table':
                table_config = sub_elemento.config
                break
        
        if not table_config:
            # Si no hay sub_elementos, usar la configuración del elemento principal
            table_config = {
                'model_class': elemento_config.model,
                'columns': [],  # Se debe configurar en el elemento
                'api_url': f'/{self.registro_config.app_namespace}/api/{paso_config.nombre}/',
                'allow_create': True,
                'allow_edit': True,
                'allow_delete': True,
                'page_length': 10
            }
        
        # Crear elemento de tabla editable
        table_elemento = EditableTableElemento(registro, table_config)
        
        context = {
            'registro': registro,
            'paso_config': paso_config,
            'elemento_config': elemento_config,
            'elemento': table_elemento,
            'title': self.registro_config.title,
            'breadcrumbs': self.get_breadcrumbs(),
            'header_title': self.get_header_title(),
            'sub_elementos': elemento_config.sub_elementos,
        }
        
        return render(request, 'components/table_only.html', context)
    
    def handle_editable_table_post(self, request, registro, paso_config, elemento_config):
        """Maneja las operaciones POST de tablas editables."""
        # Esta función se puede usar para operaciones específicas de tabla editable
        # Por ahora, redirigir a la vista de tabla editable
        return redirect(f'{self.registro_config.app_namespace}:steps', registro_id=registro.id)


class GenericActivarRegistroView(LoginRequiredMixin, BreadcrumbsMixin, View):
    """
    Vista genérica para activar registros.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registro_config = self.get_registro_config()
    
    def get_registro_config(self) -> RegistroConfig:
        """Obtiene la configuración del registro. Debe ser sobrescrito."""
        raise NotImplementedError("Debe implementar get_registro_config()")
    
    def get(self, request):
        """Muestra el formulario de activación."""
        form = create_activar_registro_form(
            registro_model=self.registro_config.registro_model,
            title_default=self.registro_config.title,
            description_default=f'Registro {self.registro_config.title} activado desde el formulario'
        )()
        
        context = {
            'form': form,
            'title': f'Activar {self.registro_config.title}',
            'breadcrumbs': self.get_breadcrumbs(),
        }
        
        return render(request, 'components/activar_registro_form.html', context)
    
    def post(self, request):
        """Procesa la activación del registro."""
        form = create_activar_registro_form(
            registro_model=self.registro_config.registro_model,
            title_default=self.registro_config.title,
            description_default=f'Registro {self.registro_config.title} activado desde el formulario'
        )(data=request.POST)
        
        if form.is_valid():
            try:
                registro = form.save(commit=False)
                registro.user = request.user
                registro.save()
                
                messages.success(request, f'Registro {self.registro_config.title} activado exitosamente.')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Registro {self.registro_config.title} activado exitosamente.',
                        'redirect_url': f'{self.registro_config.app_namespace}:steps'
                    })
                else:
                    return redirect(f'{self.registro_config.app_namespace}:steps', registro_id=registro.id)
                    
            except Exception as e:
                messages.error(request, f'Error al activar el registro: {str(e)}')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Error al activar el registro: {str(e)}'
                    }, status=400)
                else:
                    context = {
                        'form': form,
                        'title': f'Activar {self.registro_config.title}',
                        'breadcrumbs': self.get_breadcrumbs(),
                    }
                    return render(request, 'components/activar_registro_form.html', context)
        else:
            messages.error(request, 'Error en el formulario. Por favor, corrija los errores.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Error en el formulario.',
                    'errors': form.errors
                }, status=400)
            else:
                context = {
                    'form': form,
                    'title': f'Activar {self.registro_config.title}',
                    'breadcrumbs': self.get_breadcrumbs(),
                }
                return render(request, 'components/activar_registro_form.html', context) 