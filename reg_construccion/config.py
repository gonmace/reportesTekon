"""
Configuración declarativa para registros Reporte de construcción.
"""

from registros.config import (
    create_simple_config, 
    create_registro_config,
    create_1_point_map_config,
    create_2_point_map_config,
    create_3_point_map_config,
    create_photos_config,
    create_table_config,
    create_custom_config,
    create_sub_element_only_config
)
from .models import RegConstruccion, AvanceComponente
from .forms import AvanceComponenteForm
from core.models.sites import Site

# Configuración de pasos
PASOS_CONFIG = {
    'avance_componente': create_custom_config(
        model_class=AvanceComponente,
        form_class=AvanceComponenteForm,
        title='Avance por Componente',
        description='Tabla de avances por componente de la estructura.',
        template_form='components/elemento_form.html',
        sub_elementos=[
            create_table_config(
                table_title="COMPONENTES",
                table_template='components/sub_elemento_table.html',
                data_source="avance_componente_data",
                fields_to_show=['componente', 'incidencia', 'ejec_anterior', 'ejec_actual', 'ejec_acumulada', 'ejecucion_total']
            )
        ]
    ),
}

# Configuración completa del registro
REGISTRO_CONFIG = create_registro_config(
    registro_model=RegConstruccion,
    pasos_config=PASOS_CONFIG,
    title='Reporte de construcción',
    app_namespace='reg_construccion',
    list_template='components/generic_tables2_template.html',
    steps_template='pages/steps_generic.html',
    allow_multiple_per_site=True,  # Permite múltiples registros por sitio (uno por día)
    project=True  # Muestra campo de estructura/grupo de proyectos
)