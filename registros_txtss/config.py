"""
Configuración declarativa para registros TX/TSS.
"""

from registros.config import create_site_paso_config, create_simple_paso_config, create_registro_config
from .models import Registros, RSitio, RAcceso, REmpalme
from .forms import RSitioForm, RAccesoForm, REmpalmeForm


# Configuración de pasos usando funciones genéricas
PASOS_CONFIG = {
    'sitio': create_site_paso_config(
        model_class=RSitio,
        form_class=RSitioForm,
        title='Sitio',
        description='Información general del sitio.'
    ),
    'acceso': create_simple_paso_config(
        model_class=RAcceso,
        form_class=RAccesoForm,
        fields=['tipo_suelo', 'distancia', 'comentarios'],
        title='Acceso',
        description='Información sobre el acceso al sitio.',
        photo_count=3
    ),
    'empalme': create_simple_paso_config(
        model_class=REmpalme,
        form_class=REmpalmeForm,
        fields=['proveedor', 'capacidad', 'comentarios'],
        title='Empalme',
        description='Información sobre el empalme.',
        photo_count=2
    ),
}

# Configuración completa del registro
REGISTRO_CONFIG = create_registro_config(
    registro_model=Registros,
    pasos_config=PASOS_CONFIG,
    title='TX/TSS',
    app_namespace='txtss',
    list_template='pages/main_txtss.html',
    steps_template='pages/steps_txtss.html'
) 