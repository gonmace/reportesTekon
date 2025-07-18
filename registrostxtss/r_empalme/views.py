from registrostxtss.views.generic_views import GenericRegistroView
from registrostxtss.r_empalme.models import REmpalme
from registrostxtss.r_empalme.form import REmpalmeForm


class REmpalmeView(GenericRegistroView):
    """
    Vista específica para el modelo REmpalme usando la vista genérica.
    """
    form_class = REmpalmeForm
    
    def setup(self, request, *args, **kwargs):
        """Configura la vista con el modelo REmpalme."""
        kwargs['model_class'] = REmpalme
        kwargs['etapa'] = 'empalme'
        super().setup(request, *args, **kwargs)

