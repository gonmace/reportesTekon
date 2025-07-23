from django_weasyprint.views import WeasyTemplateView
from datetime import datetime
from reg_txtss.models import RegTxtss
from django.conf import settings
from pathlib import Path
from django.shortcuts import render

class TxtssPDFView(WeasyTemplateView):
    template_name = 'reportes/txtss.html'
    # pdf_attachment = True
    # pdf_filename = 'registro_individual.pdf'
    pdf_options = {
        'default-font-family': 'Arial',
        'default-font-size': 12,
    }
    pdf_stylesheets = [str(Path(settings.BASE_DIR) / 'static/css/weasyprint.css')]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registro_id = self.kwargs.get('registro_id')

        registro = RegTxtss.objects.select_related('sitio', 'user')\
            .prefetch_related('racceso_set', 'rsitio_set', 'rempalme_set')\
            .get(id=registro_id)
            
        context.update({
            'registro': registro,
            # Ejemplo de datos para los parciales reutilizables
            'tabla_equipos': {
                'headers': ['Equipo', 'Modelo', 'Estado'],
                'rows': [
                    ['Antena', '18 dBi, 5.8 GHz', 'Instalada'],
                    ['Router', 'RB3011UiAS', 'Configurado'],
                ]
            },
            'lista_materiales': [
                'Cable coaxial 10m',
                'Conectores tipo N',
                'Soporte de antena',
            ],
            'imagen_sitio': {
                'src': '/static/img/sitio_ejemplo.jpg',
                'alt': 'Foto del sitio',
                'caption': 'Vista general del sitio.'
            },
            'mapa_ubicacion': {
                'src': '/static/img/mapa_ejemplo.png',
                'alt': 'Mapa de ubicación',
                'caption': 'Ubicación geográfica del sitio.'
            },
        })
        return context


def preview_registro_individual(request, registro_id):
    registro = RegTxtss.objects.select_related('sitio', 'user')\
        .prefetch_related('racceso_set', 'rsitio_set', 'rempalme_set')\
        .get(id=registro_id)
    
    context = {
        'registro': registro,
        # Ejemplo de datos para los parciales reutilizables
        'tabla_equipos': {
            'headers': ['Equipo', 'Modelo', 'Estado'],
            'rows': [
                ['Antena', '18 dBi, 5.8 GHz', 'Instalada'],
                ['Router', 'RB3011UiAS', 'Configurado'],
            ]
        },
        'lista_materiales': [
            'Cable coaxial 10m',
            'Conectores tipo N',
            'Soporte de antena',
        ],
        'imagen_sitio': {
            'src': '/static/img/sitio_ejemplo.jpg',
            'alt': 'Foto del sitio',
            'caption': 'Vista general del sitio.'
        },
        'mapa_ubicacion': {
            'src': '/static/img/mapa_ejemplo.png',
            'alt': 'Mapa de ubicación',
            'caption': 'Ubicación geográfica del sitio.'
        },
    }
    return render(request, 'reportes/txtss.html', context)