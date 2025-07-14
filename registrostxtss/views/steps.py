from django.views import View
from django.shortcuts import render, get_object_or_404
from registrostxtss.models.main_registrostxtss import RegistrosTxTss
from registrostxtss.r_sitio.models import RSitio
from photos.models import Photos

class StepsRegistroView(View):
    def get(self, request, registro_id):
        
        registro_txtss = get_object_or_404(RegistrosTxTss, id=registro_id)
        
        # Obtener la instancia de RSitio relacionada con este registro
        try:
            rsitio = RSitio.objects.get(registro=registro_txtss)
            rsitio_id = rsitio.id
        except RSitio.DoesNotExist:
            rsitio_id = None

        # SITIO
        completeness_info = RSitio.check_completeness(rsitio_id)
        etapa = RSitio.get_etapa()
        try:
            photo_count = Photos.get_photo_count_and_color(registro_id, etapa=etapa)
            color = 'success' if photo_count >= 4 else 'warning'
            
        except Photos.DoesNotExist:
            photo_count = 0
            color = 'error'
        
        context_sitio = {
                'registro_id': registro_id,
                'completeness_info': completeness_info,
                'photo': {
                    'count': photo_count,
                    'color': color
                }
        }
        
        # ACCESO
        
        
        context = {
            'sitio': context_sitio,
        }
        return render(request, 'pages/steps.html', context)