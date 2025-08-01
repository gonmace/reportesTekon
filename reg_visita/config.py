"""
Configuración declarativa para registros Reporte de visita.
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
from .models import RegVisita, Visita, Avance
from .forms import VisitaForm, AvanceForm
from core.models.sites import Site

# Configuración de pasos
PASOS_CONFIG = {
    'visita': create_custom_config(
        model_class=Visita,
        form_class=VisitaForm,
        title='Visita',
        description='Información sobre visita.',
        template_form='components/elemento_form.html'
    ),
    'avance': create_custom_config(
        model_class=Avance,
        form_class=AvanceForm,
        title='Avance',
        description='Información sobre avance.',
        template_form='components/elemento_form.html'
    ),
}

# Configuración completa del registro
REGISTRO_CONFIG = create_registro_config(
    registro_model=RegVisita,
    pasos_config=PASOS_CONFIG,
    title='Reporte de visita',
    app_namespace='reg_visita',
    list_template='pages/main_generic.html',
    steps_template='pages/steps_generic.html'
)