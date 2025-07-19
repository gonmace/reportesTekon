from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from registrostxtss.models.registrostxtss import MapasGoogle, RegistrosTxTss
from photos.models import Photos
from core.utils.breadcrumbs import BreadcrumbsMixin
from abc import ABC, abstractmethod
from core.utils.coordenadas import calcular_distancia_geopy
from typing import Dict, Any, Optional, Tuple


class BaseStepsView(BreadcrumbsMixin, TemplateView, ABC):
    """
    Vista base abstracta para manejar pasos de registro de manera genérica.
    
    Esta clase proporciona la funcionalidad base para crear vistas de pasos
    que pueden manejar diferentes tipos de contextos (con y sin fotos, mapas, etc.).
    
    Características principales:
    - Gestión automática de fotos y su estado
    - Sistema de mapas genérico y configurable
    - Cálculo de desfases entre coordenadas
    - Verificación de completitud de pasos
    
    Para usar esta clase, hereda de ella y define:
    - template_name: El template a usar
    - get_steps_config(): La configuración de los pasos
    - get_breadcrumbs(): Los breadcrumbs específicos
    """
    
    @abstractmethod
    def get_steps_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Define la configuración de los pasos del registro.
        Cada paso puede tener fotos o no, y diferentes configuraciones.
        
        Returns:
            dict: Configuración de los pasos con la siguiente estructura:
            {
                'step_name': {
                    'model_class': ModelClass,
                    'has_photos': bool (opcional, default: False),
                    'min_photo_count': int (opcional, default: 4),
                    'desfase': bool (opcional),
                    'map': {
                        'coordinates_1': {
                            'model': str,  # 'site', 'current', o nombre del modelo ('rsitio', 'racceso', etc.)
                            'lat': str,    # nombre del campo de latitud
                            'lon': str,    # nombre del campo de longitud
                            'label': str,  # etiqueta para mostrar
                            'color': str,  # color del marcador (opcional, default: '#3B82F6')
                            'size': str    # tamaño del marcador (opcional, default: 'large')
                        },
                        'coordinates_2': {
                            'model': str,  # 'site', 'current', o nombre del modelo
                            'lat': str,    # nombre del campo de latitud
                            'lon': str,    # nombre del campo de longitud
                            'label': str,  # etiqueta para mostrar
                            'color': str,  # color del marcador (opcional, default: '#10B981')
                            'size': str    # tamaño del marcador (opcional, default: 'mid')
                        },
                        'coordinates_3': {
                            'model': str,  # 'site', 'current', o nombre del modelo
                            'lat': str,    # nombre del campo de latitud
                            'lon': str,    # nombre del campo de longitud
                            'label': str,  # etiqueta para mostrar
                            'color': str,  # color del marcador (opcional, default: '#8B5CF6')
                            'size': str    # tamaño del marcador (opcional, default: 'mid')
                        }
                        # Se pueden agregar más coordenadas: coordinates_4, coordinates_5, etc.
                    }
                }
            }
        """
        pass
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Genera el contexto principal de la vista."""
        context = super().get_context_data(**kwargs)
        
        registro_id = self.kwargs.get('registro_id')
        registro_txtss = get_object_or_404(RegistrosTxTss, id=registro_id)
        
        # Generar contexto para cada paso
        steps_config = self.get_steps_config()
        steps_context = self._generate_steps_context(registro_txtss, steps_config)
        
        context.update(steps_context)
        return context
    
    def _generate_steps_context(self, registro_txtss: RegistrosTxTss, steps_config: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Genera el contexto para todos los pasos."""
        steps_context = {}
        
        for step_name, config in steps_config.items():
            steps_context[step_name] = self._generate_single_step_context(registro_txtss, config)
        
        return steps_context
    
    def _generate_single_step_context(self, registro_txtss: RegistrosTxTss, config: Dict[str, Any]) -> Dict[str, Any]:
        """Genera el contexto para un paso específico."""
        model_class = config['model_class']
        has_photos = config.get('has_photos', False)  # default a False
        min_photo_count = config.get('min_photo_count', 4)
        
        # Obtener instancia y información básica
        instance, instance_id = self._get_model_instance(model_class, registro_txtss)
        completeness_info = model_class.check_completeness(instance_id)
        etapa = model_class.get_etapa()
        
        # Contexto base
        step_context = {
            'registro_id': registro_txtss.id,
            'completeness_info': completeness_info,
        }
        
        # Agregar información de fotos si es necesario
        if has_photos:
            step_context['photo'] = self._get_photo_info(registro_txtss.id, etapa, min_photo_count)
        
        # Agregar información de desfase si está configurado
        if config.get('desfase') and instance:
            step_context['desfase'] = self._get_desfase_info(registro_txtss.sitio, instance)
        
        # Procesar configuración del mapa si existe
        if config.get('map'):
            step_context['map'] = self._get_map_info(registro_txtss, model_class, etapa, completeness_info, config['map'])
        
        return step_context
    
    def _get_model_instance(self, model_class, registro_txtss: RegistrosTxTss) -> Tuple[Optional[Any], Optional[int]]:
        """Obtiene la instancia del modelo y su ID."""
        try:
            instance = model_class.objects.get(registro=registro_txtss)
            return instance, instance.id
        except model_class.DoesNotExist:
            return None, None
    
    def _get_photo_info(self, registro_id: int, etapa: str, min_photo_count: int) -> Dict[str, Any]:
        """Obtiene la información de fotos para un paso."""
        try:
            photo_count = Photos.get_photo_count_and_color(registro_id, etapa=etapa)
            color = self._get_photo_color(photo_count, min_photo_count)
        except Photos.DoesNotExist:
            photo_count = 0
            color = 'error'
        
        return {
            'count': photo_count,
            'color': color
        }
    
    def _get_photo_color(self, photo_count: int, min_photo_count: int) -> str:
        """Determina el color basado en el número de fotos."""
        if photo_count >= min_photo_count:
            return 'success'
        elif photo_count == 0:
            return 'error'
        else:
            return 'warning'
    
    def _get_desfase_info(self, site, instance) -> Dict[str, Any]:
        """Obtiene la información de desfase entre el sitio base y la inspección."""
        try:
            desfase = calcular_distancia_geopy(site.lat_base, site.lon_base, instance.lat, instance.lon)
            color = self._get_desfase_color(desfase)
            
            return {
                'distancia': round(desfase) if desfase else "",
                'color': color if desfase else "",
                'lat_base': site.lat_base,
                'lon_base': site.lon_base,
                'lat_inspeccion': instance.lat,
                'lon_inspeccion': instance.lon,
            }
        except (AttributeError, TypeError):
            return {
                'distancia': "",
                'color': ""
            }
    
    def _get_desfase_color(self, desfase: float) -> str:
        """Determina el color del desfase basado en la distancia."""
        if desfase < 10:
            return 'success'
        elif desfase <= 30:
            return 'warning'
        else:
            return 'error'
    
    def _get_map_info(self, registro_txtss: RegistrosTxTss, model_class, etapa: str, 
                      completeness_info: Dict[str, Any], map_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Obtiene la información del mapa para un paso."""
        # Verificar estado del mapa
        map_status = self._get_map_status(registro_txtss, etapa, completeness_info)
        
        # Obtener coordenadas
        coordinates = self._get_map_coordinates(registro_txtss, model_class, map_config)
        
        if not coordinates:
            return None
        
        map_info = {
            'status': map_status,
            'etapa': etapa,
            'coordinates_1': coordinates['coord1']
        }
        
        # Agregar todas las coordenadas adicionales
        for i in range(2, 10):  # Soporte para hasta 9 coordenadas
            coord_key = f'coord{i}'
            if coord_key in coordinates:
                map_info[f'coordinates_{i}'] = coordinates[coord_key]
        
        return map_info
    
    def _get_map_status(self, registro_txtss: RegistrosTxTss, etapa: str, 
                       completeness_info: Dict[str, Any]) -> str:
        """Determina el estado del mapa (success, error, disabled)."""
        try:
            mapas_google = MapasGoogle.objects.filter(registro=registro_txtss, etapa=etapa).first()
            return 'success' if mapas_google else 'error'
        except MapasGoogle.DoesNotExist:
            return 'error' if completeness_info['filled_fields'] > 0 else 'disabled'
    
    def _get_map_coordinates(self, registro_txtss: RegistrosTxTss, model_class, 
                            map_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Obtiene las coordenadas para el mapa."""
        try:
            site = registro_txtss.sitio
            instance = model_class.objects.get(registro=registro_txtss)
            
            coordinates = {}
            
            # Obtener todas las coordenadas configuradas
            for i in range(1, 10):  # Soporte para hasta 9 coordenadas
                coord_key = f'coordinates_{i}'
                if coord_key in map_config:
                    coord = self._get_coordinate_from_config(site, instance, map_config[coord_key], registro_txtss)
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
            
        except (model_class.DoesNotExist, AttributeError) as e:
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
            lat = getattr(instance, lat_field, None)
            lon = getattr(instance, lon_field, None)
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
            'rsitio': 'registrostxtss.r_sitio.models.RSitio',
            'racceso': 'registrostxtss.r_acceso.models.RAcceso',
            'rempalme': 'registrostxtss.r_empalme.models.REmpalme',
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
            {'label': 'TX/TSS', 'url_name': 'registrostxtss:list'}
        ]
        
        # Obtener el nombre del sitio del registro
        registro_id = self.kwargs.get('registro_id')
        if registro_id:
            try:
                registro_txtss = get_object_or_404(RegistrosTxTss, id=registro_id)
                sitio_cod = self._get_sitio_codigo(registro_txtss)
                breadcrumbs.append({'label': sitio_cod})
            except RegistrosTxTss.DoesNotExist:
                breadcrumbs.append({'label': 'Steps'})
        else:
            breadcrumbs.append({'label': 'Steps'})
        
        return self._resolve_breadcrumbs(breadcrumbs)
    
    def _get_sitio_codigo(self, registro_txtss: RegistrosTxTss) -> str:
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
        from registrostxtss.r_sitio.models import RSitio
        from registrostxtss.r_acceso.models import RAcceso
        from registrostxtss.r_empalme.models import REmpalme
        
        return {
            'sitio': {
                'model_class': RSitio,
                'has_photos': True,
                'min_photo_count': 4,
                'desfase': True,
                'map': {
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
            'acceso': {
                'model_class': RAcceso,
                'map': {
                    'coordinates_1': {
                        'model': 'current',
                        'lat': 'lat',
                        'lon': 'lon',
                        'label': 'Acceso',
                        'color': '#8B5CF6',
                        'size': 'large',
                    },
                    # No se especifica coordinates_2 - solo se muestra un punto
                }
            },
            'empalme': {
                'model_class': REmpalme,
                'has_photos': True,
                'min_photo_count': 3,
                'map': {
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
        }