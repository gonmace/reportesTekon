from django_weasyprint.views import WeasyTemplateView
from datetime import datetime
from reg_txtss.models import RegTxtss
from django.conf import settings
from pathlib import Path
from django.shortcuts import render
from core.models.google_maps import GoogleMapsImage
from django.contrib.contenttypes.models import ContentType
from reg_txtss.config import PASOS_CONFIG

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



class RegistroPDFView(WeasyTemplateView):
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
        
        paso_sitio = registro.rsitio_set.first()
        paso_sitio_lat = paso_sitio.lat
        paso_sitio_lon = paso_sitio.lon
        
        paso_acceso = registro.racceso_set.first()
        
        paso_empalme = registro.rempalme_set.first()
        paso_empalme_lat = paso_empalme.lat
        paso_empalme_lon = paso_empalme.lon
        
        # Obtener el mapa del paso sitio desde la base de datos
        # Los mapas se guardan asociados al registro principal (RegTxtss), no a los pasos individuales
        registro_content_type = ContentType.objects.get_for_model(registro)
        mapa_sitio = GoogleMapsImage.objects.filter(
            content_type=registro_content_type,
            object_id=registro.id,
            etapa='sitio'
        ).first()
        
        # Obtener el mapa del empalme desde la base de datos
        # Los mapas se guardan asociados al registro principal (RegTxtss), no a los pasos individuales
        mapa_empalme = GoogleMapsImage.objects.filter(
            content_type=registro_content_type,
            object_id=registro.id,
            etapa='empalme'
        ).first()
        
        # Obtener configuración del mapa de sitio desde PASOS_CONFIG
        sitio_config = PASOS_CONFIG['sitio']
        sitio_mapa_config = None
        for sub_elemento in sitio_config.elemento.sub_elementos:
            if sub_elemento.tipo == 'mapa':
                sitio_mapa_config = sub_elemento
                break
        
        # Extraer valores de la configuración del mapa de sitio
        sitio_icon1_color = sitio_mapa_config.config.get('icon_config', {}).get('color', '#FFFF44') if sitio_mapa_config else '#FFFF44'
        sitio_name1 = sitio_mapa_config.config.get('name_field', 'Inspección') if sitio_mapa_config else 'Inspección'
        
        # Extraer valores del segundo punto si existe
        sitio_icon2_color = None
        sitio_name2 = None
        if sitio_mapa_config and 'second_model' in sitio_mapa_config.config:
            sitio_icon2_color = sitio_mapa_config.config['second_model'].get('icon_config', {}).get('color', '#0054FF')
            sitio_name2 = sitio_mapa_config.config['second_model'].get('name_field', 'Mandato')
        
        # Obtener configuración del mapa de empalme desde PASOS_CONFIG
        empalme_config = PASOS_CONFIG['empalme']
        empalme_mapa_config = None
        for sub_elemento in empalme_config.elemento.sub_elementos:
            if sub_elemento.tipo == 'mapa':
                empalme_mapa_config = sub_elemento
                break
        
        # Extraer valores de la configuración del mapa de empalme (3 puntos)
        empalme_icon1_color = empalme_mapa_config.config.get('icon_config', {}).get('color', '#FF4040') if empalme_mapa_config else '#FF4040'
        empalme_name1 = empalme_mapa_config.config.get('name_field', 'Empalme') if empalme_mapa_config else 'Empalme'
        
        # Extraer valores del segundo punto si existe
        empalme_icon2_color = None
        empalme_name2 = None
        if empalme_mapa_config and 'second_model' in empalme_mapa_config.config:
            empalme_icon2_color = empalme_mapa_config.config['second_model'].get('icon_config', {}).get('color', '#FFFF44')
            empalme_name2 = empalme_mapa_config.config['second_model'].get('name_field', 'Inspección')
        
        # Extraer valores del tercer punto si existe
        empalme_icon3_color = None
        empalme_name3 = None
        if empalme_mapa_config and 'third_model' in empalme_mapa_config.config:
            empalme_icon3_color = empalme_mapa_config.config['third_model'].get('icon_config', {}).get('color', '#0054FF')
            empalme_name3 = empalme_mapa_config.config['third_model'].get('name_field', 'Mandato')
            
        desfase = mapa_sitio.distancia_total_metros
        if desfase < 5:
            desfase_color = '#90EE90'
        elif desfase <= 30:
            desfase_color = '#FFFF44'
        else:
            desfase_color = '#FF4040'
            
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
                'Fecha de Inspección:': registro.created_at.strftime('%d/%m/%Y'), # TODO: cambiar a fecha de inspección
            },
            'datos_geograficos': {
                'headers': ['Ubicación', 'Latitud (°)', 'Latitud (DMS)', 'Longitud (°)', 'Longitud (DMS)'],
                'rows': [
                    ['Mandato', registro.sitio.lat_base, convert_lat_to_dms(registro.sitio.lat_base), registro.sitio.lon_base, convert_lon_to_dms(registro.sitio.lon_base)],
                    ['Inspección', paso_sitio_lat, convert_lat_to_dms(paso_sitio_lat), paso_sitio_lon, convert_lon_to_dms(paso_sitio_lon)],
                    ['Empalme', paso_empalme_lat, convert_lat_to_dms(paso_empalme_lat), paso_empalme_lon, convert_lon_to_dms(paso_empalme_lon)],
                ]
            },
            
            'registro_sitio': {
                f'{paso_sitio._meta.get_field("altura").verbose_name}:': f'{paso_sitio.altura} m',
                f'{paso_sitio._meta.get_field("deslindes").verbose_name}:': f'{paso_sitio.deslindes} metros',
                f'{paso_sitio._meta.get_field("comentarios").verbose_name}:': f'{paso_sitio.comentarios}',
            },
            
            'google_sitio_image': {
                'src': mapa_sitio.imagen.url if mapa_sitio else None,
                'alt': 'Mapa de ubicación del sitio',
                'desfase': f'{mapa_sitio.distancia_total_metros:.0f} m',
                'desfase_color': desfase_color,
                'icon1_color': sitio_icon1_color,
                'name1': sitio_name1,
                'icon2_color': sitio_icon2_color,
                'name2': sitio_name2
            },
            
            'registro_sitio_fotos': {
                'fotos': self._get_sitio_photos(registro)
            },
            
            'registro_acceso': {
                f'{paso_acceso._meta.get_field("tipo_suelo").verbose_name}:': f'{paso_acceso.tipo_suelo}',
                f'{paso_acceso._meta.get_field("distancia").verbose_name}:': f'{paso_acceso.distancia} metros',
                f'{paso_acceso._meta.get_field("comentarios").verbose_name}:': f'{paso_acceso.comentarios}',
            },
            'registro_empalme': {
                f'{paso_empalme._meta.get_field("proveedor").verbose_name}:': f'{paso_empalme.proveedor}',
                f'{paso_empalme._meta.get_field("capacidad").verbose_name}:': f'{paso_empalme.capacidad}',
                f'{paso_empalme._meta.get_field("comentarios").verbose_name}:': f'{paso_empalme.comentarios}',
            },
            
            'google_empalme_image': {
                'src': mapa_empalme.imagen.url if mapa_empalme else None,
                'alt': 'Mapa de ubicación del empalme',
                'caption': f'Distancia Sitio-Empalme: {mapa_empalme.distancia_total_metros:.0f} m' if mapa_empalme else 'Mapa no disponible',
                'icon1_color': empalme_icon1_color,
                'name1': empalme_name1,
                'icon2_color': empalme_icon2_color,
                'name2': empalme_name2,
                'icon3_color': empalme_icon3_color,
                'name3': empalme_name3
            },

        })
        return context

    def _get_sitio_photos(self, registro):
        """
        Obtiene todas las fotos relacionadas con el registro_sitio.
        Para la etapa 'sitio', las fotos se asocian al registro principal (RegTxtss).
        """
        from photos.models import Photos
        from django.contrib.contenttypes.models import ContentType
        
        # Obtener el ContentType del modelo del registro principal
        registro_content_type = ContentType.objects.get_for_model(registro)
        
        # Obtener todas las fotos para este registro, etapa 'sitio' y app 'reg_txtss'
        fotos = Photos.objects.filter(
            content_type=registro_content_type,
            object_id=registro.id,
            etapa='sitio',
            app='reg_txtss'
        ).order_by('orden', '-created_at')
        
        # Convertir a formato para el template
        fotos_list = []
        for foto in fotos:
            fotos_list.append({
                'src': foto.imagen.url,
                'alt': foto.descripcion or f'Foto del sitio {registro.sitio.pti_cell_id}',
                'descripcion': foto.descripcion,
                'orden': foto.orden
            })
        
        return fotos_list

def preview_registro_individual(request, registro_id):
    # Crear una instancia temporal de la vista para reutilizar get_context_data
    view = RegistroPDFView()
    view.kwargs = {'registro_id': registro_id}
    context = view.get_context_data()
    
    print('--------------------------------')
    print(context)
    print('--------------------------------')
    return render(request, 'reportes/txtss.html', context)