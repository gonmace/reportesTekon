from django.views import View
from django.shortcuts import render, get_object_or_404
from registrostxtss.models.main_registrostxtss import RegistrosTxTss
from registrostxtss.r_sitio.models import RSitio


class StepsRegistroView(View):
    def get(self, request, registro_id):
        
        registro_txtss = get_object_or_404(RegistrosTxTss, id=registro_id)
        
        # Obtener la instancia de RSitio relacionada con este registro
        try:
            rsitio = RSitio.objects.get(registro=registro_txtss)
            rsitio_id = rsitio.id
        except RSitio.DoesNotExist:
            rsitio_id = None

        completeness_info = RSitio.check_completeness(rsitio_id)
        
        context = {
            'registro_id': registro_id,
            'registro_txtss': registro_txtss,
            'completeness_info': completeness_info,
        }
        return render(request, 'pages/steps.html', context)