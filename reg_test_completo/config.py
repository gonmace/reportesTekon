"""
Configuración declarativa para registros Test Completo.
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
from .models import RegTestCompleto, Paso1, Paso2, Paso3
from .forms import Paso1Form, Paso2Form, Paso3Form
from core.models.sites import Site

# Configuración de pasos
PASOS_CONFIG = {
    'paso1': create_custom_config(
        model_class=Paso1,
        form_class=Paso1Form,
        title='Paso1',
        description='Información sobre paso1.',
        template_form='components/elemento_form.html'
    ),
    'paso2': create_custom_config(
        model_class=Paso2,
        form_class=Paso2Form,
        title='Paso2',
        description='Información sobre paso2.',
        template_form='components/elemento_form.html'
    ),
    'paso3': create_custom_config(
        model_class=Paso3,
        form_class=Paso3Form,
        title='Paso3',
        description='Información sobre paso3.',
        template_form='components/elemento_form.html'
    ),
}

# Configuración completa del registro
REGISTRO_CONFIG = create_registro_config(
    registro_model=RegTestCompleto,
    pasos_config=PASOS_CONFIG,
    title='Test Completo',
    app_namespace='reg_test_completo',
    list_template='reg_test_completo/list.html',
    steps_template='reg_test_completo/steps.html'
)