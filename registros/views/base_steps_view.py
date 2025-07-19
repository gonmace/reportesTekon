from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from registros.models.registrostxtss import MapasGoogle, Registros
from photos.models import Photos
from core.utils.breadcrumbs import BreadcrumbsMixin
from abc import ABC, abstractmethod
from core.utils.coordenadas import calcular_distancia_geopy
from typing import Dict, Any, Optional, Tuple, List


class BaseStepsView(BreadcrumbsMixin, TemplateView, ABC):
    """
    Vista base abstracta para manejar pasos de registro de manera genérica.
    
    Esta clase proporciona la funcionalidad base para crear vistas de pasos
    que pueden manejar diferentes tipos de contextos de manera completamente configurable.
    
    Características principales:
    - Gestión automática de fotos y su estado
    - Sistema de mapas genérico y configurable
    - Cálculo de desfases entre coordenadas
    - Verificación de completitud de pasos
    - Sistema de elementos configurable por step
    
    Para usar esta clase, hereda de ella y define:
    - template_name: El template a usar
    - get_steps_config(): La configuración de los pasos
    - get_breadcrumbs(): Los breadcrumbs específicos
    """
    
    @abstractmethod
    def get_steps_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Define la configuración de los pasos del registro.
        Cada paso puede tener cualquier combinación de elementos configurados.
        
        Returns:
            dict: Configuración de los pasos con la siguiente estructura:
            {
                'step_name': {
                    'model_class': ModelClass,
                    'elements': {
                        'form': bool,  # Siempre True (requerido)
                        'photos': {
                            'enabled': bool,  # Si el step tiene fotos
                            'min_count': int,  # Mínimo de fotos requeridas (default: 4)
                            'required': bool,  # Si las fotos son obligatorias (default: False)
                        },
                        'map': {
                            'enabled': bool,  # Si el step tiene mapa
                            'coordinates': {
                                'coordinates_1': {
                                    'model': str,  # 'site', 'current', o nombre del modelo
                                    'lat': str,    # nombre del campo de latitud
                                    'lon': str,    # nombre del campo de longitud
                                    'label': str,  # etiqueta para mostrar
                                    'color': str,  # color del marcador (opcional)
                                    'size': str    # tamaño del marcador (opcional)
                                },
                                # ... más coordenadas hasta coordinates_9
                            }
                        },
                        'desfase': {
                            'enabled': bool,  # Si calcular desfase entre puntos
                            'reference': str,  # 'site' para usar sitio base como referencia
                            'description': str,  # Descripción del desfase (opcional)
                        }
                    },
                    'order': int,  # Orden de aparición (opcional, default: orden alfabético)
                    'title': str,  # Título personalizado (opcional, default: step_name)
                    'description': str,  # Descripción del step (opcional)
                }
            }
        """
        pass
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Genera el contexto principal de la vista."""
        context = super().get_context_data(**kwargs)
        
        registro_id = self.kwargs.get('registro_id')
        registro_txtss = get_object_or_404(Registros, id=registro_id)
        
        # Generar contexto para cada paso
        steps_config = self.get_steps_config()
        steps_context = self._generate_steps_context(registro_txtss, steps_config)
        
        # Ordenar los steps según la configuración
        ordered_steps = self._order_steps(steps_context, steps_config)
        
        context.update({
            'steps': ordered_steps,
            'steps_config': steps_config,
            'registro_txtss': registro_txtss,
        })
        return context
    
    def _order_steps(self, steps_context: Dict[str, Any], steps_config: Dict[str, Dict[str, Any]]) -> List[Tuple[str, Dict[str, Any]]]:
        """Ordena los steps según la configuración."""
        # Crear lista de tuplas (step_name, step_data) con orden
        steps_with_order = []
        for step_name, step_data in steps_context.items():
            config = steps_config.get(step_name, {})
            order = config.get('order', 999)  # Default alto para steps sin orden
            steps_with_order.append((step_name, step_data, order))
        
        # Ordenar por orden y luego alfabéticamente
        steps_with_order.sort(key=lambda x: (x[2], x[0]))
        
        # Retornar solo (step_name, step_data)
        return [(name, data) for name, data, _ in steps_with_order]
    
    def _generate_steps_context(self, registro_txtss: Registros, steps_config: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Genera el contexto para todos los pasos."""
        steps_context = {}
        
        for step_name, config in steps_config.items():
            steps_context[step_name] = self._generate_single_step_context(registro_txtss, config, step_name)
        
        return steps_context
    
    def _generate_single_step_context(self, registro_txtss: Registros, config: Dict[str, Any], step_name: str) -> Dict[str, Any]:
        """Genera el contexto para un paso específico."""
        model_class = config['model_class']
        elements_config = config.get('elements', {})
        
        # Obtener instancia y información básica
        instance, instance_id = self._get_model_instance(model_class, registro_txtss)
        completeness_info = model_class.check_completeness(instance_id)
        etapa = model_class.get_etapa()
        
        # Contexto base
        step_context = {
            'registro_id': registro_txtss.id,
            'completeness_info': completeness_info,
            'step_name': step_name,
            'title': config.get('title', step_name.title()),
            'description': config.get('description', ''),
            'etapa': etapa,
            'elements': {
                # El formulario siempre está presente
                'form': {
                    'enabled': True,
                    'url': self._get_form_url(step_name, registro_txtss.id),
                    'color': completeness_info['color']
                }
            },
        }
        
        # Procesar elementos opcionales
        if 'photos' in elements_config and elements_config['photos'].get('enabled', False):
            step_context['elements']['photos'] = self._get_photos_element(
                registro_txtss.id, etapa, elements_config['photos']
            )
        
        if 'map' in elements_config and elements_config['map'].get('enabled', False):
            map_info = self._get_map_element(
                registro_txtss, model_class, etapa, completeness_info, elements_config['map']
            )
            if map_info:
                step_context['elements']['map'] = map_info
        
        if 'desfase' in elements_config and elements_config['desfase'].get('enabled', False):
            if instance:
                step_context['elements']['desfase'] = self._get_desfase_element(
                    registro_txtss.sitio, instance, elements_config['desfase']
                )
        
        return step_context
    
    def _get_form_url(self, step_name: str, registro_id: int) -> str:
        """Genera la URL del formulario para el step."""
        # Mapeo de nombres de step a URLs
        step_urls = {
            'sitio': 'registros:r_sitio',
            'acceso': 'registros:r_acceso',
            'empalme': 'registros:r_empalme',
        }
        
        url_name = step_urls.get(step_name, f'registros:r_{step_name}')
        return f'/registros/{registro_id}/{step_name}/'
    
    def _get_photos_element(self, registro_id: int, etapa: str, photos_config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene la configuración del elemento de fotos."""
        min_count = photos_config.get('min_count', 4)
        required = photos_config.get('required', False)
        
        try:
            photo_count = Photos.get_photo_count_and_color(registro_id, etapa=etapa)
            color = self._get_photo_color(photo_count, min_count)
        except Photos.DoesNotExist:
            photo_count = 0
            color = 'error'
        
        return {
            'enabled': True,
            'count': photo_count,
            'color': color,
            'min_count': min_count,
            'required': required,
            'url': f'/registros/{registro_id}/{etapa}/photos/'
        }
    
    def _get_map_element(self, registro_txtss: Registros, model_class, etapa: str, 
                         completeness_info: Dict[str, Any], map_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Obtiene la configuración del elemento de mapa."""
        coordinates_config = map_config.get('coordinates', {})
        
        # Verificar estado del mapa
        map_status = self._get_map_status(registro_txtss, etapa, completeness_info)
        
        # Obtener coordenadas
        coordinates = self._get_map_coordinates(registro_txtss, model_class, coordinates_config)
        
        if not coordinates:
            return None
        
        map_info = {
            'enabled': True,
            'status': map_status,
            'etapa': etapa,
            'coordinates': coordinates
        }
        
        return map_info
    
    def _get_desfase_element(self, site, instance, desfase_config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene la configuración del elemento de desfase."""
        try:
            desfase = calcular_distancia_geopy(site.lat_base, site.lon_base, instance.lat, instance.lon)
            color = self._get_desfase_color(desfase)
            
            return {
                'enabled': True,
                'distancia': round(desfase) if desfase else "",
                'color': color if desfase else "",
                'description': desfase_config.get('description', ''),
                'lat_base': site.lat_base,
                'lon_base': site.lon_base,
                'lat_inspeccion': instance.lat,
                'lon_inspeccion': instance.lon,
            }
        except (AttributeError, TypeError):
            return {
                'enabled': True,
                'distancia': "",
                'color': "",
                'description': desfase_config.get('description', '')
            }
    
    def _get_model_instance(self, model_class, registro_txtss: Registros) -> Tuple[Optional[Any], Optional[int]]:
        """Obtiene la instancia del modelo y su ID."""
        try:
            instance = model_class.objects.get(registro=registro_txtss)
            return instance, instance.id
        except model_class.DoesNotExist:
            return None, None
    
    def _get_photo_color(self, photo_count: int, min_photo_count: int) -> str:
        """Determina el color basado en el número de fotos."""
        if photo_count >= min_photo_count:
            return 'success'
        elif photo_count == 0:
            return 'error'
        else:
            return 'warning'
    
    def _get_desfase_color(self, desfase: float) -> str:
        """Determina el color del desfase basado en la distancia."""
        if desfase < 10:
            return 'success'
        elif desfase <= 30:
            return 'warning'
        else:
            return 'error'
    
    def _get_map_status(self, registro_txtss: Registros, etapa: str, 
                       completeness_info: Dict[str, Any]) -> str:
        """Determina el estado del mapa (success, error, disabled)."""
        try:
            mapas_google = MapasGoogle.objects.filter(registro=registro_txtss, etapa=etapa).first()
            return 'success' if mapas_google else 'error'
        except MapasGoogle.DoesNotExist:
            return 'error' if completeness_info['filled_fields'] > 0 else 'disabled'
    
    def _get_map_coordinates(self, registro_txtss: Registros, model_class, 
                            coordinates_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Obtiene las coordenadas para el mapa."""
        try:
            site = registro_txtss.sitio
            
            # Intentar obtener la instancia del modelo, pero no fallar si no existe
            try:
                instance = model_class.objects.get(registro=registro_txtss)
            except model_class.DoesNotExist:
                instance = None
            
            coordinates = {}
            
            # Obtener todas las coordenadas configuradas
            for i in range(1, 10):  # Soporte para hasta 9 coordenadas
                coord_key = f'coordinates_{i}'
                if coord_key in coordinates_config:
                    coord = self._get_coordinate_from_config(site, instance, coordinates_config[coord_key], registro_txtss)
                    print(f"DEBUG - Coordenada {i}: {coord}")  # Debug
                    if coord['lat'] and coord['lon']:
                        coordinates[f'coord{i}'] = coord
                        print(f"DEBUG - Coordenada {i} válida agregada")  # Debug
                    else:
                        print(f"DEBUG - Coordenada {i} inválida: lat={coord['lat']}, lon={coord['lon']}")  # Debug
            
            # Verificar que al menos la primera coordenada sea válida
            if not coordinates:
                print("DEBUG - No se encontraron coordenadas válidas")  # Debug
                return None
            
            print(f"DEBUG - Coordenadas finales: {list(coordinates.keys())}")  # Debug
            return coordinates
            
        except AttributeError as e:
            print(f"DEBUG - Error obteniendo coordenadas: {e}")  # Debug
            return None
    
    def _get_coordinate_from_config(self, site, instance, coord_config: Dict[str, Any], registro_txtss=None) -> Dict[str, Any]:
        """Obtiene una coordenada específica basada en la configuración."""
        lat_field = coord_config['lat']
        lon_field = coord_config['lon']
        label = coord_config['label']
        color = coord_config.get('color', '#3B82F6')  # default azul
        size = coord_config.get('size', 'large')  # default large
        model_source = coord_config.get('model', 'current')  # default a 'current'
        
        print(f"DEBUG - Obteniendo coordenada: model={model_source}, lat_field={lat_field}, lon_field={lon_field}")  # Debug
        
        # Determinar de dónde obtener las coordenadas
        if model_source == 'site':
            # Coordenadas del sitio base
            lat = getattr(site, lat_field, None)
            lon = getattr(site, lon_field, None)
            print(f"DEBUG - Coordenadas del sitio: lat={lat}, lon={lon}")  # Debug
        elif model_source == 'current':
            # Coordenadas del modelo actual
            if instance:
                lat = getattr(instance, lat_field, None)
                lon = getattr(instance, lon_field, None)
            else:
                lat, lon = None, None
            print(f"DEBUG - Coordenadas del modelo actual: lat={lat}, lon={lon}")  # Debug
        else:
            # Coordenadas de un modelo específico
            if registro_txtss:
                lat, lon = self._get_coordinates_from_specific_model(registro_txtss, model_source, lat_field, lon_field)
                print(f"DEBUG - Coordenadas del modelo específico {model_source}: lat={lat}, lon={lon}")  # Debug
            else:
                lat, lon = None, None
        
        return {
            'lat': lat,
            'lon': lon,
            'label': label,
            'color': color,
            'size': size
        }
    
    def _get_coordinates_from_specific_model(self, registro, model_name: str, lat_field: str, lon_field: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Obtiene coordenadas de un modelo específico.
        
        Args:
            registro: Instancia del registro principal
            model_name: Nombre del modelo ('rsitio', 'racceso', 'rempalme', etc.)
            lat_field: Nombre del campo de latitud
            lon_field: Nombre del campo de longitud
            
        Returns:
            Tuple con latitud y longitud, o (None, None) si hay error
        """
        try:
            # Obtener la clase del modelo dinámicamente
            model_class = self._get_model_class_by_name(model_name)
            if not model_class:
                return None, None
            
            # Obtener la instancia del modelo
            model_instance = model_class.objects.get(registro=registro)
            
            lat = getattr(model_instance, lat_field, None)
            lon = getattr(model_instance, lon_field, None)
            
            return lat, lon
            
        except (ImportError, model_class.DoesNotExist, AttributeError):
            return None, None
    
    def _get_model_class_by_name(self, model_name: str):
        """
        Obtiene la clase del modelo por su nombre.
        
        Para agregar nuevos modelos, simplemente agrega una nueva condición aquí.
        
        Args:
            model_name: Nombre del modelo
            
        Returns:
            Clase del modelo o None si no se encuentra
        """
        model_mapping = {
            'rsitio': 'registros.r_sitio.models.RSitio',
            'racceso': 'registros.r_acceso.models.RAcceso',
            'rempalme': 'registros.r_empalme.models.REmpalme',
        }
        
        if model_name not in model_mapping:
            return None
        
        try:
            # Importar dinámicamente el modelo
            module_path, class_name = model_mapping[model_name].rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)
        except (ImportError, AttributeError):
            return None


class StepsRegistroView(BaseStepsView):
    """
    Vista específica para los pasos del registro Tx/TSS.
    Hereda de BaseStepsView para reutilizar la funcionalidad común.
    """
    
    template_name = 'pages/steps_txtss.html'
    
    def get_breadcrumbs(self):
        """Genera breadcrumbs dinámicos con el nombre del sitio."""
        breadcrumbs = [
            {'label': 'Inicio', 'url_name': 'dashboard:dashboard'},
            {'label': 'Registros', 'url_name': 'registros:list'}
        ]
        
        # Obtener el nombre del sitio del registro
        registro_id = self.kwargs.get('registro_id')
        if registro_id:
            try:
                registro_txtss = get_object_or_404(Registros, id=registro_id)
                sitio_cod = self._get_sitio_codigo(registro_txtss)
                breadcrumbs.append({'label': sitio_cod})
            except Registros.DoesNotExist:
                breadcrumbs.append({'label': 'Steps'})
        else:
            breadcrumbs.append({'label': 'Steps'})
        
        return self._resolve_breadcrumbs(breadcrumbs)
    
    def _get_sitio_codigo(self, registro_txtss: Registros) -> str:
        """Obtiene el código del sitio para los breadcrumbs."""
        try:
            return registro_txtss.sitio.pti_cell_id
        except AttributeError:
            try:
                return registro_txtss.sitio.operator_id
            except AttributeError:
                return 'Sitio'
    
    def get_steps_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Define la configuración de los pasos del registro Tx/TSS.
        
        Configuración de mapas:
        - 'model': 'site' = usar coordenadas del sitio base (lat_base, lon_base)
        - 'model': 'current' = usar coordenadas del modelo actual del paso
        - 'model': 'rsitio' = usar coordenadas del modelo RSitio
        - 'model': 'racceso' = usar coordenadas del modelo RAcceso
        - 'model': 'rempalme' = usar coordenadas del modelo REmpalme
        
        Returns:
            dict: Configuración de los pasos
        """
        from registros.r_sitio.models import RSitio
        from registros.r_acceso.models import RAcceso
        from registros.r_empalme.models import REmpalme
        
        return {
            'sitio': {
                'model_class': RSitio,
                'order': 1,
                'title': 'Sitio',
                'description': 'Información general del sitio.',
                'elements': {
                    'photos': {
                        'enabled': True,
                        'min_count': 4,
                        'required': False,
                    },
                    'map': {
                        'enabled': True,
                        'coordinates': {
                            'coordinates_1': {
                                'model': 'site',  
                                'lat': 'lat_base',
                                'lon': 'lon_base',
                                'label': 'Mandato',
                                'color': '#3B82F6',
                                'size': 'large',   
                            },
                            'coordinates_2': {
                                'model': 'current',
                                'lat': 'lat',
                                'lon': 'lon',
                                'label': 'Inspección',
                                'color': '#F59E0B',
                                'size': 'mid',
                            },
                        }
                    },
                    'desfase': {
                        'enabled': True,
                        'reference': 'site',
                        'description': 'Desfase respecto mandato',
                    }
                },
            },
            'acceso': {
                'model_class': RAcceso,
                'order': 2,
                'title': 'Acceso',
                'description': 'Información sobre el acceso al sitio.',
            },
            'empalme': {
                'model_class': REmpalme,
                'order': 3,
                'title': 'Empalme',
                'description': 'Información sobre el empalme.',
                'elements': {
                    'photos': {
                        'enabled': True,
                        'min_count': 3,
                        'required': False,
                    },
                    'map': {
                        'enabled': True,
                        'coordinates': {
                            'coordinates_1': {
                                'model': 'rsitio', 
                                'lat': 'lat',
                                'lon': 'lon',
                                'label': 'Sitio',
                                'color': '#F59E0B',
                                'size': 'large',   
                            },
                            'coordinates_2': {
                                'model': 'current',
                                'lat': 'lat',
                                'lon': 'lon',
                                'label': 'Empalme',
                                'color': '#e60000',
                                'size': 'mid',     
                            },
                            'coordinates_3': {
                                'model': 'site',
                                'lat': 'lat_base',
                                'lon': 'lon_base',
                                'label': 'Mandato',
                                'color': '#3B82F6',
                                'size': 'large',     
                            },
                        }
                    },
                    'desfase': {
                        'enabled': True,
                        'reference': 'site',
                        'description': 'Distancia Sitio a Empalme',
                    }
                },
            },
        }