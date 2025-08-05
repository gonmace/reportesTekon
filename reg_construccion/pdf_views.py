from django_weasyprint.views import WeasyTemplateView
from datetime import datetime
from reg_construccion.models import RegConstruccion
from django.conf import settings
from pathlib import Path
from django.shortcuts import render
from core.models.google_maps import GoogleMapsImage
from django.contrib.contenttypes.models import ContentType
from reg_construccion.config import PASOS_CONFIG

def convert_lat_to_dms(lat):
    direction = 'N' if lat >= 0 else 'S'
    deg_abs = abs(lat)
    degrees = int(deg_abs)
    minutes_full = (deg_abs - degrees) * 60
    minutes = int(minutes_full)
    seconds = round((minutes_full - minutes) * 60, 2)
    return f"{direction} {degrees}° {minutes}' {seconds}''"

def convert_lon_to_dms(lon):
    direction = 'E' if lon >= 0 else 'W'
    deg_abs = abs(lon)
    degrees = int(deg_abs)
    minutes_full = (deg_abs - degrees) * 60
    minutes = int(minutes_full)
    seconds = round((minutes_full - minutes) * 60, 2)
    return f"{direction} {degrees}° {minutes}' {seconds}''"

class RegConstruccionPDFView(WeasyTemplateView):
    template_name = 'reportes_reg_construccion/reg_visita.html'
    pdf_options = {
        'default-font-family': 'Arial',
        'default-font-size': 12,
        'enable-local-file-access': True,
    }
    pdf_stylesheets = [str(Path(settings.BASE_DIR) / 'static/css/weasyprint.css')]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registro_id = self.kwargs.get('registro_id')

        registro = RegConstruccion.objects.select_related('sitio', 'user')\
            .prefetch_related('visita_set', 'avance_set')\
            .get(id=registro_id)
        
        # Datos generales
        context.update({
            'registro': registro,
            'datos_generales': {
                f'Código {registro.sitio._meta.get_field("pti_cell_id").verbose_name}:': registro.sitio.pti_cell_id,
                f'Código {registro.sitio._meta.get_field("operator_id").verbose_name}:': registro.sitio.operator_id,
                f'{registro.sitio._meta.get_field("name").verbose_name}:': registro.sitio.name,
                f'{registro.sitio._meta.get_field("lat_base").verbose_name}:': registro.sitio.lat_base,
                f'{registro.sitio._meta.get_field("lon_base").verbose_name}:': registro.sitio.lon_base, 
                f'{registro.sitio._meta.get_field("region").verbose_name}:': registro.sitio.region,
                f'{registro.sitio._meta.get_field("comuna").verbose_name}:': registro.sitio.comuna,
            },
            'inspeccion_sitio': {
                'Responsable Técnico:': registro.user.first_name + ' ' + registro.user.last_name,
                'Fecha de Inspección:': registro.created_at.strftime('%d/%m/%Y'),
            },
        })
        
        # Agregar datos de cada paso
        
        # Datos del paso visita
        paso_visita = registro.visita_set.first()
        if paso_visita:
            registro_visita_data = {}
            for field in paso_visita._meta.fields:
                if field.name not in ['id', 'created_at', 'updated_at', 'registro']:
                    value = getattr(paso_visita, field.name)
                    if value is not None and value != '':
                        registro_visita_data[f'{field.verbose_name}:'] = str(value)
            
            context['registro_visita'] = registro_visita_data
            
            # Mapa del visita
            registro_content_type = ContentType.objects.get_for_model(registro)
            mapa_visita = GoogleMapsImage.objects.filter(
                content_type=registro_content_type,
                object_id=registro.id,
                etapa='visita'
            ).first()
            
            if mapa_visita:
                context['google_visita_image'] = {
                    'src': mapa_visita.imagen.url,
                    'alt': f'Mapa de {paso}',
                    'caption': f'Distancia: {mapa_visita.distancia_total_metros:.0f} m' if mapa_visita.distancia_total_metros else '',
                    'icon1_color': '#FF4040',
                    'name1': 'Visita',
                }
            else:
                context['google_visita_image'] = {'src': None}
            
            # Fotos del visita
            context['registro_visita_fotos'] = {
                'fotos': self._get_photos(registro, 'visita')
            }
        else:
            context['registro_visita'] = {}
            context['google_visita_image'] = {'src': None}
            context['registro_visita_fotos'] = {'fotos': []}
        # Datos del paso avance
        paso_avance = registro.avance_set.first()
        if paso_avance:
            registro_avance_data = {}
            for field in paso_avance._meta.fields:
                if field.name not in ['id', 'created_at', 'updated_at', 'registro']:
                    value = getattr(paso_avance, field.name)
                    if value is not None and value != '':
                        registro_avance_data[f'{field.verbose_name}:'] = str(value)
            
            context['registro_avance'] = registro_avance_data
            
            # Mapa del avance
            registro_content_type = ContentType.objects.get_for_model(registro)
            mapa_avance = GoogleMapsImage.objects.filter(
                content_type=registro_content_type,
                object_id=registro.id,
                etapa='avance'
            ).first()
            
            if mapa_avance:
                context['google_avance_image'] = {
                    'src': mapa_avance.imagen.url,
                    'alt': f'Mapa de {paso}',
                    'caption': f'Distancia: {mapa_avance.distancia_total_metros:.0f} m' if mapa_avance.distancia_total_metros else '',
                    'icon1_color': '#FF4040',
                    'name1': 'Avance',
                }
            else:
                context['google_avance_image'] = {'src': None}
            
            # Fotos del avance
            context['registro_avance_fotos'] = {
                'fotos': self._get_photos(registro, 'avance')
            }
        else:
            context['registro_avance'] = {}
            context['google_avance_image'] = {'src': None}
            context['registro_avance_fotos'] = {'fotos': []}
        
        return context

    def _get_photos(self, registro, etapa):
        """Obtiene todas las fotos relacionadas con el registro para una etapa específica."""
        from photos.models import Photos
        from django.contrib.contenttypes.models import ContentType
        
        registro_content_type = ContentType.objects.get_for_model(registro)
        
        fotos = Photos.objects.filter(
            content_type=registro_content_type,
            object_id=registro.id,
            etapa=etapa,
            app='reg_construccion'
        ).order_by('orden', '-created_at')
        
        fotos_list = []
        for foto in fotos:
            fotos_list.append({
                'src': foto.imagen.url,
                'alt': foto.descripcion or f'Foto de {etapa} {registro.sitio.pti_cell_id}',
                'descripcion': foto.descripcion,
                'orden': foto.orden
            })
        
        return fotos_list

def preview_reg_construccion_individual(request, registro_id):
    view = RegConstruccionPDFView()
    view.kwargs = {'registro_id': registro_id}
    context = view.get_context_data()
    return render(request, 'reportes_reg_construccion/reg_visita.html', context)
