"""
Tablas genéricas para registros.
"""

import django_tables2 as tables
from django_tables2 import A
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from registros.models.base import RegistroBase

User = get_user_model()

class GenericRegistrosTable(tables.Table):
    """
    Tabla genérica para mostrar registros.
    Puede ser configurada para cualquier aplicación que herede de RegistroBase.
    """
    
    # Columnas básicas
    pti_id = tables.Column(
        accessor='sitio.pti_cell_id',
        verbose_name='PTI ID',
        attrs={'td': {'class': 'text-center'}, 'th': {'class': 'text-center'}}
    )
    
    operador_id = tables.Column(
        accessor='sitio.operator_id',
        verbose_name='Operador ID',
        attrs={'td': {'class': 'text-center'}, 'th': {'class': 'text-center'}}
    )
    
    nombre_sitio = tables.Column(
        accessor='sitio.name',
        verbose_name='Nombre Sitio',
        attrs={'td': {'class': 'w-fit max-w-40'}}
    )
    
    # Columna ITO (solo para superusuarios)
    ito = tables.Column(
        accessor='user.username',
        verbose_name='ITO',
        attrs={'td': {'class': 'text-center'}, 'th': {'class': 'text-center'}},
        empty_values=()
    )
    
    # Columna de acciones
    acciones = tables.TemplateColumn(
        template_name='components/registro_actions.html',
        verbose_name='Acciones',
        attrs={'td': {'class': 'text-center'}, 'th': {'class': 'text-center'}},
        orderable=False
    )
    
    class Meta:
        template_name = "django_tables2/bootstrap5.html"
        attrs = {
            'class': 'table table-sm table-zebra w-full',
            'thead': {'class': 'bg-accent text-white uppercase'},
        }
        fields = ('pti_id', 'operador_id', 'nombre_sitio')
        sequence = ('pti_id', 'operador_id', 'nombre_sitio')
        orderable = True
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.app_namespace = kwargs.pop('app_namespace', 'registros')
        super().__init__(*args, **kwargs)
        
        # Agregar columnas adicionales para superusuarios
        if self.user and self.user.is_superuser:
            self.base_columns['ito'] = self.ito
            self.base_columns['acciones'] = self.acciones
            self.Meta.sequence = ('pti_id', 'operador_id', 'nombre_sitio', 'ito', 'acciones')
    
    def render_ito(self, value, record):
        """Renderizar la columna ITO con funcionalidad de edición para superusuarios."""
        if self.user and self.user.is_superuser:
            return format_html(
                '<div class="ito-cell-container">'
                '<span class="ito-text" style="cursor: pointer;" data-registro-id="{}">'
                '{} <i class="fa-solid fa-pen-to-square text-xs text-warning ml-1"></i></span>'
                '<select class="ito-select select select-warning select-sm select-bordered w-full max-w-full" '
                'style="display: none;" data-registro-id="{}">'
                '<option value="">Seleccionar ITO</option>'
                '</select></div>',
                record.id,
                value or "Sin asignar",
                record.id
            )
        return value or "Sin asignar"


def create_registros_table(model_class, app_namespace='registros'):
    """
    Factory function para crear una tabla específica para un modelo de registro.
    
    Args:
        model_class: Clase del modelo que hereda de RegistroBase
        app_namespace: Namespace de la aplicación para las URLs
    
    Returns:
        Clase de tabla configurada
    """
    class SpecificRegistrosTable(GenericRegistrosTable):
        class Meta(GenericRegistrosTable.Meta):
            model = model_class
    
    return SpecificRegistrosTable 