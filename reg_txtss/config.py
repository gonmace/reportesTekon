"""
Configuración declarativa para registros TX/TSS.
"""

from registros.config import create_photo_map_config, create_photo_config, create_simple_config, create_registro_config
from .models import RegTxtss, RSitio, RAcceso, REmpalme
from .forms import RSitioForm, RAccesoForm, REmpalmeForm


# Configuración de pasos usando funciones genéricas
PASOS_CONFIG = {
    'sitio': create_photo_map_config(
        model_class=RSitio,
        form_class=RSitioForm,
        title='Sitio',
        description='Información general del sitio.',
        photo_min=4
    ),
    'acceso': create_simple_config(
        model_class=RAcceso,
        form_class=RAccesoForm,
        title='Acceso',
        description='Información sobre el acceso al sitio.'
    ),
    'empalme': create_photo_config(
        model_class=REmpalme,
        form_class=REmpalmeForm,
        title='Empalme',
        description='Información sobre el empalme.',
        photo_min=2
    ),
}

# Configuración completa del registro
REGISTRO_CONFIG = create_registro_config(
    registro_model=RegTxtss,
    pasos_config=PASOS_CONFIG,
    title='TX/TSS',
    app_namespace='reg_txtss',
    list_template='pages/main_txtss.html',
    steps_template='pages/steps_txtss.html'
) 