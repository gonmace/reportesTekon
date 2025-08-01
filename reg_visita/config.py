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
from .models import RegVisita, AvanceProyecto
from core.models.sites import Site

# Configuración de columnas para tabla editable de avances de proyecto
avances_proyecto_columns = [
    {
        'key': 'proyecto',
        'label': 'Estructura Proyecto',
        'type': 'select',
        'editable': True,
        'required': False,
        'options_api': '/reg_visita/api/estructuras_proyecto/',  # API para cargar opciones dinámicamente
        'display_field': 'nombre',  # Campo a mostrar en el select
        'value_field': 'id'  # Campo a usar como valor
    },
    {
        'key': 'componente',
        'label': 'Componente',
        'type': 'select',
        'editable': True,
        'required': False,
        'options_api': '/reg_visita/api/componentes/',  # API para cargar opciones dinámicamente
        'display_field': 'nombre',  # Campo a mostrar en el select
        'value_field': 'id'  # Campo a usar como valor
    },
    {
        'key': 'comentarios',
        'label': 'Comentarios',
        'type': 'text',
        'editable': True,
        'required': False
    },
    {
        'key': 'ejecucion_anterior',
        'label': '% Ejecución Anterior',
        'type': 'number',
        'editable': True,
        'required': True,
        'min': 0,
        'max': 100,
        'step': 0.01
    },
    {
        'key': 'ejecucion_actual',
        'label': '% Ejecución Actual',
        'type': 'number',
        'editable': True,
        'required': True,
        'min': 0,
        'max': 100,
        'step': 0.01
    },
    {
        'key': 'ejecucion_acumulada',
        'label': '% Ejecución Acumulada',
        'type': 'number',
        'editable': True,
        'required': True,
        'min': 0,
        'step': 0.01
    },
    {
        'key': 'ejecucion_total',
        'label': '% Ejecución Total',
        'type': 'number',
        'editable': True,
        'required': True,
        'min': 0,
        'step': 0.01
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
    'avance_proyecto': create_table_only_config(
        title='Avances de Proyecto',
        description='Administre los avances de ejecución de proyectos. Puede editar los porcentajes de ejecución y seleccionar la estructura de proyecto y componente relacionado directamente en la tabla.',
        columns=avances_proyecto_columns,
        model_class=AvanceProyecto,
        template_name='components/editable_table.html',  # Usar directamente el template de tabla editable
        api_url='/reg_visita/api/avances_proyecto/',
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