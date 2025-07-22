from django_weasyprint.views import WeasyTemplateView
from datetime import datetime
from reg_txtss.models import RegTxtss
from django.conf import settings
from pathlib import Path
from django.shortcuts import render

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
            
        context.update({
            'registro': registro,
        })
        return context

def preview_registro_individual(request, registro_id):
    registro = RegTxtss.objects.select_related('sitio', 'user')\
        .prefetch_related('racceso_set', 'rsitio_set', 'rempalme_set')\
        .get(id=registro_id)
    
    context = {
        'registro': registro,
    }
    return render(request, 'reportes/txtss.html', context)