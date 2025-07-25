"""
Configuración declarativa para registros Mantenimiento Preventivo.
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
from .models import RegMantenimiento, Inspeccion, Diagnostico, Reparacion, Pruebas, Verificacion
from .forms import InspeccionForm, DiagnosticoForm, ReparacionForm, PruebasForm, VerificacionForm
from core.models.sites import Site

# Configuración de pasos
PASOS_CONFIG = {
    'inspeccion': create_custom_config(
        model_class=Inspeccion,
        form_class=InspeccionForm,
        title='Inspeccion',
        description='Información sobre inspeccion.',
        template_form='components/elemento_form.html'
    ),
    'diagnostico': create_custom_config(
        model_class=Diagnostico,
        form_class=DiagnosticoForm,
        title='Diagnostico',
        description='Información sobre diagnostico.',
        template_form='components/elemento_form.html'
    ),
    'reparacion': create_custom_config(
        model_class=Reparacion,
        form_class=ReparacionForm,
        title='Reparacion',
        description='Información sobre reparacion.',
        template_form='components/elemento_form.html'
    ),
    'pruebas': create_custom_config(
        model_class=Pruebas,
        form_class=PruebasForm,
        title='Pruebas',
        description='Información sobre pruebas.',
        template_form='components/elemento_form.html'
    ),
    'verificacion': create_custom_config(
        model_class=Verificacion,
        form_class=VerificacionForm,
        title='Verificacion',
        description='Información sobre verificacion.',
        template_form='components/elemento_form.html'
    ),
}

# Configuración completa del registro
REGISTRO_CONFIG = create_registro_config(
    registro_model=RegMantenimiento,
    pasos_config=PASOS_CONFIG,
    title='Mantenimiento Preventivo',
    app_namespace='reg_mantenimiento',
    list_template='reg_mantenimiento/list.html',
    steps_template='reg_mantenimiento/steps.html'
)