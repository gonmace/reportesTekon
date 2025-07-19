from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.utils.breadcrumbs import BreadcrumbsMixin
from registros.views.base_steps_view import BaseStepsView
from registros.models.registrostxtss import Registros
from registros.forms.activar import ActivarRegistroForm
from typing import Dict, Any


class ListRegistrosView(LoginRequiredMixin, BreadcrumbsMixin, TemplateView):
    template_name = 'pages/main_txtss.html'
    context_object_name = 'registros'

    class Meta:
        title = 'Registros Tx/Tss'
        header_title = 'Registros Tx/Tss'
        breadcrumbs = [
            {'label': 'Inicio', 'url_name': 'dashboard:dashboard'},
            {'label': 'TX/TSS'}
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ActivarRegistroForm()
        return context


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
            {'label': 'Registros TX/TSS', 'url_name': 'registros_txtss:list'}
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
        from .r_sitio.models import RSitio
        from .r_acceso.models import RAcceso
        from .r_empalme.models import REmpalme
        
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
