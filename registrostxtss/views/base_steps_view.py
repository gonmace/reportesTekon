from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from registrostxtss.models.registrostxtss import MapasGoogle, RegistrosTxTss
from photos.models import Photos
from core.utils.breadcrumbs import BreadcrumbsMixin
from abc import ABC, abstractmethod
from core.utils.coordenadas import calcular_distancia_geopy

class BaseStepsView(BreadcrumbsMixin, TemplateView, ABC):
    """
    Vista base abstracta para manejar pasos de registro de manera genérica.
    
    Esta clase proporciona la funcionalidad base para crear vistas de pasos
    que pueden manejar diferentes tipos de contextos (con y sin fotos).
    
    Para usar esta clase, hereda de ella y define:
    - template_name: El template a usar
    - get_steps_config(): La configuración de los pasos
    - get_breadcrumbs(): Los breadcrumbs específicos
    """
    
    @abstractmethod
    def get_steps_config(self):
        """
        Define la configuración de los pasos del registro.
        Cada paso puede tener fotos o no, y diferentes configuraciones.
        
        Returns:
            dict: Configuración de los pasos con la siguiente estructura:
            {
                'step_name': {
                    'model_class': ModelClass,
                    'has_photos': bool,
                    'min_photo_count': int (opcional, default: 4)
                }
            }
        """
        pass
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        registro_id = self.kwargs.get('registro_id')
        registro_txtss = get_object_or_404(RegistrosTxTss, id=registro_id)
        
        # Definir la configuración de los pasos
        steps_config = self.get_steps_config()
        
        # Generar contexto para cada paso
        steps_context = {}
        for step_name, config in steps_config.items():
            steps_context[step_name] = self.generate_step_context(
                registro_txtss, 
                config['model_class'], 
                config['has_photos'], 
                config.get('min_photo_count', 4),
                config.get('desfase'),
                config.get('dist_empalme'),
                config.get('map_desfase')
            )
        
        context.update(steps_context)
        return context
    
    def generate_step_context(self, registro_txtss, model_class, has_photos, min_photo_count=4, desfase=None, dist_empalme=None, map_desfase=False):
        """
        Genera el contexto para un paso específico.
        
        Args:
            registro_txtss: Instancia del registro principal
            model_class: Clase del modelo del paso
            has_photos: Si el paso tiene fotos
            min_photo_count: Número mínimo de fotos requeridas
            desfase: Información de desfase (opcional)
            dist_empalme: Información de distancia a empalme (opcional)
        Returns:
            dict: Contexto del paso
        """
        # Obtener la instancia del modelo relacionada con este registro
        try:
            instance = model_class.objects.get(registro=registro_txtss)
            instance_id = instance.id
        except model_class.DoesNotExist:
            instance_id = None
        
        # Obtener información de completitud
        completeness_info = model_class.check_completeness(instance_id)
        etapa = model_class.get_etapa()
        
        # Contexto base
        step_context = {
            'registro_id': registro_txtss.id,
            'completeness_info': completeness_info,
        }
        
                # Agregar información de fotos si es necesario
        if has_photos:
            try:
                photo_count = Photos.get_photo_count_and_color(registro_txtss.id, etapa=etapa)
                if photo_count >= min_photo_count:
                    color = 'success'
                elif photo_count == 0:
                    color = 'error'
                else:
                    color = 'warning'
            except Photos.DoesNotExist:
                photo_count = 0
                color = 'error'
            
            step_context['photo'] = {
                'count': photo_count,
                'color': color
            }

        # Agregar información de desfase si existe
        if desfase:
            try:
                site = registro_txtss.sitio
                desfase = calcular_distancia_geopy(site.lat_base, site.lon_base, instance.lat, instance.lon)
                color = 'success' if desfase < 10 else 'warning' if desfase <= 30 else 'error'
                step_context['desfase'] = {
                    'distancia': round(desfase) if desfase else "",
                    'color': color if desfase else "",
                    'lat_base': site.lat_base,
                    'lon_base': site.lon_base,
                    'lat_inspeccion': instance.lat,
                    'lon_inspeccion': instance.lon,
                }
            except:
                desfase = None
                step_context['desfase'] = {
                    'distancia': "",
                    'color': ""
                }

            
        if dist_empalme:
            step_context['dist_empalme'] = dist_empalme
        
        if map_desfase:
            try:
                mapas_google = MapasGoogle.objects.filter(registro=registro_txtss, etapa=etapa).first()
                if mapas_google:
                    step_context['map_desfase'] = 'success'
                else:
                    step_context['map_desfase'] = 'error'
            except MapasGoogle.DoesNotExist:                
                if completeness_info['filled_fields'] > 0:
                    step_context['map_desfase'] = 'error'
                else:
                    step_context['map_desfase'] = 'disabled'
        
        return step_context


class StepsRegistroView(BaseStepsView):
    """
    Vista específica para los pasos del registro Tx/TSS.
    Hereda de BaseStepsView para reutilizar la funcionalidad común.
    """
    class Meta:
        title = 'Pasos del Registro'
        header_title = 'Pasos del Registro'

    template_name = 'pages/txtss_steps.html'
    
    def get_breadcrumbs(self):
        """Genera breadcrumbs dinámicos con el nombre del sitio"""
        breadcrumbs = [
            {'label': 'Inicio', 'url_name': 'dashboard:dashboard'},
            {'label': 'TX/TSS', 'url_name': 'registrostxtss:list'}
        ]
        
        # Obtener el nombre del sitio del registro
        registro_id = self.kwargs.get('registro_id')
        if registro_id:
            try:
                registro_txtss = get_object_or_404(RegistrosTxTss, id=registro_id)
                try:
                    sitio_cod = registro_txtss.sitio.pti_cell_id
                    breadcrumbs.append({'label': sitio_cod})
                except:
                    sitio_cod = registro_txtss.sitio.operator_id
                    breadcrumbs.append({'label': sitio_cod})
                    
            except RegistrosTxTss.DoesNotExist:
                breadcrumbs.append({'label': 'Steps'})
        else:
            breadcrumbs.append({'label': 'Steps'})
        
        # Resolver las URLs usando el método del mixin
        return self._resolve_breadcrumbs(breadcrumbs)
    
    def get_steps_config(self):
        """
        Define la configuración de los pasos del registro Tx/TSS.
        
        Returns:
            dict: Configuración de los pasos
        """
        
        from registrostxtss.r_sitio.models import RSitio
        from registrostxtss.r_acceso.models import RAcceso
        from registrostxtss.r_empalme.models import REmpalme

        dist_empalme = None
        
        return {
            'sitio': {
                'model_class': RSitio,
                'has_photos': True,
                'min_photo_count': 4,
                'desfase': True,
                'map_desfase': True
            },
            'acceso': {
                'model_class': RAcceso,
                'has_photos': False
            },
            'empalme': {
                'model_class': REmpalme,
                'has_photos': True,
                'min_photo_count': 3,
            },
        } 