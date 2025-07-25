"""
Configuración declarativa para registros Instalación.
"""

from registros.config import (
    create_simple_config, 
    create_registro_config,
    create_1_point_map_config,
    create_2_point_map_config,
    create_3_point_map_config,
    create_photos_config,
    create_custom_config,
    create_sub_element_only_config
)
from .models import RegInstalacion, Sitio, Acceso, Empalme
from .forms import SitioForm, AccesoForm, EmpalmeForm
from core.models.sites import Site

# Configuración de pasos
PASOS_CONFIG = {
    'sitio': create_custom_config(
        model_class=Sitio,
        form_class=SitioForm,
        title='Sitio',
        description='Información sobre sitio.',
        template_form='components/elemento_form.html'
    ),
    'acceso': create_custom_config(
        model_class=Acceso,
        form_class=AccesoForm,
        title='Acceso',
        description='Información sobre acceso.',
        template_form='components/elemento_form.html'
    ),
    'empalme': create_custom_config(
        model_class=Empalme,
        form_class=EmpalmeForm,
        title='Empalme',
        description='Información sobre empalme.',
        template_form='components/elemento_form.html'
    ),
}

# Configuración completa del registro
REGISTRO_CONFIG = create_registro_config(
    registro_model=RegInstalacion,
    pasos_config=PASOS_CONFIG,
    title='Instalación',
    app_namespace='reg_instalacion',
    list_template='reg_instalacion/list.html',
    steps_template='reg_instalacion/steps.html'
)