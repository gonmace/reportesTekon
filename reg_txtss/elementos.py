"""
Elementos específicos para registros TX/TSS.
"""

from registros.elementos.base import ElementoBase
from .models import RSitio, RAcceso, REmpalme
from .forms import RSitioForm, RAccesoForm, REmpalmeForm


class ElementoSitio(ElementoBase):
    """Elemento para el paso Sitio."""
    model = RSitio
    form_class = RSitioForm
    tipo = 'sitio'
    template_name = 'components/elemento_form.html'
    success_message = "Datos del sitio guardados exitosamente."
    error_message = "Error al guardar los datos del sitio."


class ElementoAcceso(ElementoBase):
    """Elemento para el paso Acceso."""
    model = RAcceso
    form_class = RAccesoForm
    tipo = 'acceso'
    template_name = 'components/elemento_form.html'
    success_message = "Datos de acceso guardados exitosamente."
    error_message = "Error al guardar los datos de acceso."


class ElementoEmpalme(ElementoBase):
    """Elemento para el paso Empalme."""
    model = REmpalme
    form_class = REmpalmeForm
    tipo = 'empalme'
    template_name = 'components/elemento_form.html'
    success_message = "Datos de empalme guardados exitosamente."
    error_message = "Error al guardar los datos de empalme." 