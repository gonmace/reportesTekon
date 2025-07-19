from registros.views.generic_views import GenericRegistroView
from registros.r_sitio.models import RSitio
from registros.r_sitio.form import RSitioForm


class RSitioView(GenericRegistroView):
    """
    Vista específica para el modelo RSitio usando la vista genérica.
    """
    form_class = RSitioForm
    
    def setup(self, request, *args, **kwargs):
        """Configura la vista con el modelo RSitio."""
        kwargs['model_class'] = RSitio
        kwargs['etapa'] = 'sitio'
        super().setup(request, *args, **kwargs)

