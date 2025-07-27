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
    create_sub_element_only_config,
    create_table_only_config
)
from .models import RegVisita, Visita, Avance
from .forms import VisitaForm, AvanceForm
from core.models.sites import Site

# Configuración de columnas para tabla editable de visitas
visitas_columns = [
    {
        'key': 'comentarios',
        'label': 'Comentarios',
        'type': 'text',
        'editable': True,
        'required': True
    },
    {
        'key': 'created_at',
        'label': 'Fecha Creación',
        'type': 'text',
        'editable': False
    },
    {
        'key': 'updated_at',
        'label': 'Última Actualización',
        'type': 'text',
        'editable': False
    }
]

# Configuración de columnas para tabla editable de avances
avances_columns = [
    {
        'key': 'comentarios',
        'label': 'Comentarios',
        'type': 'text',
        'editable': True,
        'required': True
    },
    {
        'key': 'created_at',
        'label': 'Fecha Creación',
        'type': 'text',
        'editable': False
    },
    {
        'key': 'updated_at',
        'label': 'Última Actualización',
        'type': 'text',
        'editable': False
    }
]

# Configuración de pasos usando tablas editables
PASOS_CONFIG = {
    'visita': create_table_only_config(
        title='Visitas',
        description='Administre las visitas realizadas. Puede editar los comentarios directamente en la tabla.',
        columns=visitas_columns,
        model_class=Visita,
        template_name='components/editable_table.html',
        api_url='/reg_visita/api/visitas/',
        allow_create=True,
        allow_edit=True,
        allow_delete=True,
        page_length=10
    ),
    'avance': create_table_only_config(
        title='Avances',
        description='Administre los avances registrados. Puede editar los comentarios directamente en la tabla.',
        columns=avances_columns,
        model_class=Avance,
        template_name='components/editable_table.html',
        api_url='/reg_visita/api/avances/',
        allow_create=True,
        allow_edit=True,
        allow_delete=True,
        page_length=10
    ),
}

# Configuración completa del registro
REGISTRO_CONFIG = create_registro_config(
    registro_model=RegVisita,
    pasos_config=PASOS_CONFIG,
    title='Reporte de visita',
    app_namespace='reg_visita',
    list_template='components/generic_tables2_template.html',
    steps_template='pages/steps_generic.html',
    allow_multiple_per_site=True  # Permite múltiples registros por sitio (uno por día)
)