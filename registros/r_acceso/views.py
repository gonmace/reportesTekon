from registros.views.generic_views import GenericRegistroView
from registros.r_acceso.models import RAcceso
from registros.r_acceso.form import RAccesoForm


class RAccesoView(GenericRegistroView):
    """
    Vista específica para el modelo RAcceso usando la vista genérica.
    """
    form_class = RAccesoForm
    
    def setup(self, request, *args, **kwargs):
        """Configura la vista con el modelo RAcceso."""
        kwargs['model_class'] = RAcceso
        kwargs['etapa'] = 'acceso'
        super().setup(request, *args, **kwargs)

