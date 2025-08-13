"""
Vistas de PDF para registros de Construcción.
"""

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
    if lat is None:
        return 'N/A'
    direction = 'N' if lat >= 0 else 'S'
    deg_abs = abs(lat)
    degrees = int(deg_abs)
    minutes_full = (deg_abs - degrees) * 60
    minutes = int(minutes_full)
    seconds = round((minutes_full - minutes) * 60, 2)
    return f"{direction} {degrees}° {minutes}' {seconds}''"

def convert_lon_to_dms(lon):
    if lon is None:
        return 'N/A'
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

        try:
            registro = RegConstruccion.objects.select_related('sitio', 'user').get(id=registro_id)
            
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
            self._add_paso_data(context, registro, 'objetivo')
            self._add_paso_data(context, registro, 'avance_componente')
            self._add_paso_data(context, registro, 'imagenes')
            
        except Exception as e:
            print(f"Error en get_context_data: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return context

    def _add_paso_data(self, context, registro, paso):
        """Agrega los datos de un paso específico al contexto."""
        # Obtener el objeto del paso
        paso_obj = None
        if paso == 'objetivo':
            paso_obj = registro.objetivo_set.first()
        elif paso == 'avance_componente':
            paso_obj = registro.avancecomponentecomentarios_set.first()
        elif paso == 'imagenes':
            # Para imágenes, no hay un modelo específico, solo fotos
            self._add_imagenes_data(context, registro)
            return
        
        if not paso_obj:
            return
        
        # Datos del paso
        paso_data = {}
        for field in paso_obj._meta.fields:
            if field.name not in ['id', 'created_at', 'updated_at', 'registro']:
                value = getattr(paso_obj, field.name)
                if value is not None and value != '':
                    paso_data[f'{field.verbose_name}:'] = str(value)
        
        context[f'registro_{paso}'] = paso_data
        
        # Mapa del paso
        registro_content_type = ContentType.objects.get_for_model(registro)
        mapa_paso = GoogleMapsImage.objects.filter(
            content_type=registro_content_type,
            object_id=registro.id,
            etapa=paso
        ).first()
        
        if mapa_paso:
            context[f'google_{paso}_image'] = {
                'src': mapa_paso.imagen.url,
                'alt': f'Mapa de {paso}',
                'caption': f'Distancia: {mapa_paso.distancia_total_metros:.0f} m' if mapa_paso.distancia_total_metros else '',
                'icon1_color': '#FF4040',
                'name1': paso.capitalize(),
            }
        else:
            context[f'google_{paso}_image'] = {'src': None}
        
        # Fotos del paso
        context[f'registro_{paso}_fotos'] = {
            'fotos': self._get_photos(registro, paso)
        }

    def _add_imagenes_data(self, context, registro):
        """Agrega los datos de imágenes al contexto."""
        context['registro_imagenes_fotos'] = {
            'fotos': self._get_photos(registro, 'imagenes')
        }

    def _get_photos(self, registro, etapa):
        """
        Obtiene todas las fotos relacionadas con una etapa específica.
        Para las etapas, las fotos se asocian al registro principal (RegConstruccion).
        """
        from photos.models import Photos
        from django.contrib.contenttypes.models import ContentType
        
        # Obtener el ContentType del modelo del registro principal
        registro_content_type = ContentType.objects.get_for_model(registro)
        
        # Obtener todas las fotos para este registro, etapa específica y app 'reg_construccion'
        fotos = Photos.objects.filter(
            content_type=registro_content_type,
            object_id=registro.id,
            etapa=etapa,
            app='reg_construccion'
        ).order_by('orden', '-created_at')
        
        # Convertir a formato para el template
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
    """Vista para previsualizar el PDF de un registro de construcción."""
    view = RegConstruccionPDFView()
    view.kwargs = {'registro_id': registro_id}
    context = view.get_context_data()
    return render(request, 'reportes_reg_construccion/reg_visita.html', context)
