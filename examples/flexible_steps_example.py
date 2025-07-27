"""
Ejemplo de uso del nuevo sistema flexible de pasos.
Este ejemplo muestra cómo crear pasos con múltiples elementos combinados.
"""

from registros.config import (
    create_flexible_step_config,
    create_form_element,
    create_table_element,
    create_map_element,
    create_photos_element,
    create_info_element,
    create_custom_element,
    create_registro_config
)
from django.db import models


# ============================================================================
# EJEMPLO 1: Paso con formulario, mapa y fotos
# ============================================================================

def ejemplo_paso_completo():
    """Ejemplo de un paso que contiene formulario, mapa y fotos."""
    
    # Definir elementos del paso
    elementos = [
        # Elemento de formulario
        create_form_element(
            model_class=MiModelo,
            form_class=MiFormulario,
            title="Información General",
            description="Complete los datos básicos del sitio",
            required=True
        ),
        
        # Elemento de mapa
        create_map_element(
            map_type="single_point",
            title="Ubicación del Sitio",
            description="Seleccione la ubicación exacta en el mapa",
            lat_field="latitud",
            lon_field="longitud",
            name_field="nombre",
            zoom=15,
            icon_color="red",
            required=True
        ),
        
        # Elemento de fotos
        create_photos_element(
            title="Fotos del Sitio",
            description="Suba al menos 4 fotos del sitio",
            min_count=4,
            max_count=10,
            required=True
        )
    ]
    
    # Crear configuración del paso
    paso = create_flexible_step_config(
        title="Información del Sitio",
        description="Complete toda la información básica del sitio incluyendo ubicación y fotos",
        elements=elementos,
        order=1
    )
    
    return paso


# ============================================================================
# EJEMPLO 2: Paso solo con tabla editable
# ============================================================================

def ejemplo_paso_tabla():
    """Ejemplo de un paso que solo contiene una tabla editable."""
    
    # Definir columnas de la tabla
    columnas = [
        {
            'name': 'nombre',
            'title': 'Nombre',
            'type': 'text',
            'required': True
        },
        {
            'name': 'descripcion',
            'title': 'Descripción',
            'type': 'textarea',
            'required': False
        },
        {
            'name': 'cantidad',
            'title': 'Cantidad',
            'type': 'number',
            'required': True
        }
    ]
    
    elementos = [
        create_table_element(
            model_class=MiTablaModel,
            title="Lista de Materiales",
            description="Agregue todos los materiales necesarios",
            columns=columnas,
            min_rows=1,
            max_rows=20,
            required=True
        )
    ]
    
    paso = create_flexible_step_config(
        title="Materiales",
        description="Gestione la lista de materiales del proyecto",
        elements=elementos,
        order=2
    )
    
    return paso


# ============================================================================
# EJEMPLO 3: Paso con información y mapa
# ============================================================================

def ejemplo_paso_informativo():
    """Ejemplo de un paso con información y mapa de referencia."""
    
    elementos = [
        # Elemento informativo
        create_info_element(
            title="Información Importante",
            content="""
            <p>Este paso muestra información de referencia sobre el mandato.</p>
            <ul>
                <li>Verifique que los datos sean correctos</li>
                <li>Confirme la ubicación en el mapa</li>
                <li>Revise los detalles del proyecto</li>
            </ul>
            """,
            icon="info",
            color="info"
        ),
        
        # Elemento de mapa de referencia
        create_map_element(
            map_type="single_point",
            title="Ubicación del Mandato",
            description="Ubicación de referencia del mandato",
            lat_field="lat_base",
            lon_field="lon_base",
            name_field="nombre",
            zoom=12,
            icon_color="blue",
            required=False
        )
    ]
    
    paso = create_flexible_step_config(
        title="Información del Mandato",
        description="Revise la información básica del mandato",
        elements=elementos,
        order=0
    )
    
    return paso


# ============================================================================
# EJEMPLO 4: Paso complejo con múltiples elementos
# ============================================================================

def ejemplo_paso_complejo():
    """Ejemplo de un paso complejo con múltiples tipos de elementos."""
    
    elementos = [
        # Formulario principal
        create_form_element(
            model_class=EmpalmeModel,
            form_class=EmpalmeForm,
            title="Datos del Empalme",
            description="Información técnica del empalme",
            required=True
        ),
        
        # Tabla de componentes
        create_table_element(
            model_class=ComponenteModel,
            title="Componentes del Empalme",
            description="Lista de componentes utilizados",
            columns=[
                {'name': 'tipo', 'title': 'Tipo', 'type': 'text', 'required': True},
                {'name': 'marca', 'title': 'Marca', 'type': 'text', 'required': True},
                {'name': 'modelo', 'title': 'Modelo', 'type': 'text', 'required': False},
                {'name': 'cantidad', 'title': 'Cantidad', 'type': 'number', 'required': True}
            ],
            min_rows=1,
            required=True
        ),
        
        # Mapa con múltiples puntos
        create_map_element(
            map_type="multi_point",
            title="Ubicación del Empalme",
            description="Ubicación del empalme y puntos de referencia",
            zoom=15,
            required=True
        ),
        
        # Fotos del empalme
        create_photos_element(
            title="Fotos del Empalme",
            description="Documente el estado del empalme con fotos",
            min_count=6,
            max_count=15,
            required=True
        ),
        
        # Información adicional
        create_info_element(
            title="Notas Importantes",
            content="Recuerde documentar cualquier anomalía encontrada durante la inspección.",
            icon="warning",
            color="warning"
        )
    ]
    
    paso = create_flexible_step_config(
        title="Empalme",
        description="Documentación completa del empalme",
        elements=elementos,
        order=3
    )
    
    return paso


# ============================================================================
# CONFIGURACIÓN COMPLETA DEL REGISTRO
# ============================================================================

def crear_configuracion_completa():
    """Crea una configuración completa de registro usando el sistema flexible."""
    
    # Definir todos los pasos
    pasos_config = {
        'mandato': ejemplo_paso_informativo(),
        'sitio': ejemplo_paso_completo(),
        'materiales': ejemplo_paso_tabla(),
        'empalme': ejemplo_paso_complejo(),
    }
    
    # Crear configuración del registro
    config = create_registro_config(
        registro_model=MiRegistroModel,
        pasos_config=pasos_config,
        title="Registro de Inspección",
        app_namespace="mi_app",
        header_title="Sistema de Inspección"
    )
    
    return config


# ============================================================================
# USO EN UNA APLICACIÓN REAL
# ============================================================================

# En tu archivo config.py de la aplicación:
"""
from registros.config import create_flexible_step_config, create_form_element, create_map_element, create_photos_element

# Configuración de pasos usando el sistema flexible
PASOS_CONFIG = {
    'sitio': create_flexible_step_config(
        title="Información del Sitio",
        description="Datos básicos y ubicación del sitio",
        elements=[
            create_form_element(
                model_class=RSitio,
                form_class=RSitioForm,
                title="Datos del Sitio",
                required=True
            ),
            create_map_element(
                title="Ubicación",
                lat_field="lat",
                lon_field="lon",
                required=True
            ),
            create_photos_element(
                title="Fotos del Sitio",
                min_count=4,
                required=True
            )
        ]
    ),
    
    'empalme': create_flexible_step_config(
        title="Empalme",
        description="Documentación del empalme",
        elements=[
            create_form_element(
                model_class=REmpalme,
                form_class=REmpalmeForm,
                title="Datos del Empalme",
                required=True
            ),
            create_map_element(
                title="Ubicación del Empalme",
                required=True
            ),
            create_photos_element(
                title="Fotos del Empalme",
                min_count=6,
                required=True
            )
        ]
    )
}

# Crear configuración del registro
REGISTRO_CONFIG = create_registro_config(
    registro_model=RVisita,
    pasos_config=PASOS_CONFIG,
    title="Registro de Visita",
    app_namespace="reg_visita"
)
""" 