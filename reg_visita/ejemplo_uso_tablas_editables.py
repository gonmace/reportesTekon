"""
Ejemplo de uso de tablas editables en reg_visita.

Este archivo muestra cómo configurar y usar tablas editables en el sistema de registros.
"""

# ============================================================================
# EJEMPLO 1: Configuración básica de tabla editable
# ============================================================================

from registros.config import create_table_only_config

# Configuración de columnas para una tabla editable
columnas_ejemplo = [
    {
        'key': 'nombre',
        'label': 'Nombre',
        'type': 'text',
        'editable': True,
        'required': True
    },
    {
        'key': 'descripcion',
        'label': 'Descripción',
        'type': 'textarea',
        'editable': True,
        'required': False
    },
    {
        'key': 'estado',
        'label': 'Estado',
        'type': 'select',
        'editable': True,
        'required': True,
        'options': [
            {'value': 'pendiente', 'label': 'Pendiente'},
            {'value': 'en_proceso', 'label': 'En Proceso'},
            {'value': 'completado', 'label': 'Completado'}
        ]
    },
    {
        'key': 'fecha_creacion',
        'label': 'Fecha de Creación',
        'type': 'date',
        'editable': False
    }
]

# Configuración de paso con tabla editable
paso_tabla_editable = create_table_only_config(
    title='Gestión de Tareas',
    description='Administre las tareas del proyecto. Puede editar los campos directamente en la tabla.',
    columns=columnas_ejemplo,
    model_class='MiModelo',  # Reemplazar con el modelo real
    template_name='components/editable_table.html',
    api_url='/mi_app/api/tareas/',
    allow_create=True,
    allow_edit=True,
    allow_delete=True,
    page_length=15
)

# ============================================================================
# EJEMPLO 2: Tabla editable con múltiples tipos de campos
# ============================================================================

columnas_avanzadas = [
    {
        'key': 'codigo',
        'label': 'Código',
        'type': 'text',
        'editable': True,
        'required': True,
        'max_length': 10
    },
    {
        'key': 'cantidad',
        'label': 'Cantidad',
        'type': 'number',
        'editable': True,
        'required': True,
        'min_value': 0
    },
    {
        'key': 'precio',
        'label': 'Precio',
        'type': 'number',
        'editable': True,
        'required': True,
        'step': 0.01
    },
    {
        'key': 'categoria',
        'label': 'Categoría',
        'type': 'select',
        'editable': True,
        'required': True,
        'options': [
            {'value': 'electronica', 'label': 'Electrónica'},
            {'value': 'ropa', 'label': 'Ropa'},
            {'value': 'hogar', 'label': 'Hogar'},
            {'value': 'deportes', 'label': 'Deportes'}
        ]
    },
    {
        'key': 'activo',
        'label': 'Activo',
        'type': 'checkbox',
        'editable': True,
        'required': False
    },
    {
        'key': 'fecha_actualizacion',
        'label': 'Última Actualización',
        'type': 'datetime',
        'editable': False
    }
]

# ============================================================================
# EJEMPLO 3: Integración en configuración de registro
# ============================================================================

from registros.config import create_registro_config

# Configuración de pasos con tabla editable
PASOS_CONFIG_EJEMPLO = {
    'informacion_basica': create_table_only_config(
        title='Información Básica',
        description='Datos básicos del registro',
        columns=[
            {
                'key': 'titulo',
                'label': 'Título',
                'type': 'text',
                'editable': True,
                'required': True
            },
            {
                'key': 'descripcion',
                'label': 'Descripción',
                'type': 'textarea',
                'editable': True,
                'required': False
            }
        ],
        model_class='RegistroBasico',
        api_url='/mi_app/api/informacion/',
        allow_create=True,
        allow_edit=True,
        allow_delete=False  # No permitir eliminar registros básicos
    ),
    
    'detalles_tecnicos': create_table_only_config(
        title='Detalles Técnicos',
        description='Información técnica del proyecto',
        columns=[
            {
                'key': 'tecnologia',
                'label': 'Tecnología',
                'type': 'select',
                'editable': True,
                'required': True,
                'options': [
                    {'value': 'python', 'label': 'Python'},
                    {'value': 'javascript', 'label': 'JavaScript'},
                    {'value': 'java', 'label': 'Java'},
                    {'value': 'csharp', 'label': 'C#'}
                ]
            },
            {
                'key': 'version',
                'label': 'Versión',
                'type': 'text',
                'editable': True,
                'required': True
            },
            {
                'key': 'complejidad',
                'label': 'Complejidad',
                'type': 'select',
                'editable': True,
                'required': True,
                'options': [
                    {'value': 'baja', 'label': 'Baja'},
                    {'value': 'media', 'label': 'Media'},
                    {'value': 'alta', 'label': 'Alta'}
                ]
            }
        ],
        model_class='DetalleTecnico',
        api_url='/mi_app/api/detalles/',
        allow_create=True,
        allow_edit=True,
        allow_delete=True
    )
}

# Configuración completa del registro
REGISTRO_CONFIG_EJEMPLO = create_registro_config(
    registro_model='MiRegistro',
    pasos_config=PASOS_CONFIG_EJEMPLO,
    title='Registro con Tablas Editables',
    app_namespace='mi_app',
    list_template='components/generic_tables2_template.html',
    steps_template='pages/steps_generic.html',
    allow_multiple_per_site=True
)

# ============================================================================
# EJEMPLO 4: Vistas personalizadas para tablas editables
# ============================================================================

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json

class TablaEditableAPIView(LoginRequiredMixin, View):
    """
    Vista API personalizada para tabla editable.
    """
    
    def get(self, request):
        """Obtener todos los registros."""
        try:
            # Obtener datos del modelo
            queryset = self.model_class.objects.filter(is_deleted=False)
            
            # Filtrar por usuario si no es superusuario
            if not request.user.is_superuser:
                queryset = queryset.filter(user=request.user)
            
            # Serializar datos
            data = []
            for obj in queryset:
                row_data = {'id': obj.id}
                for column in self.columns_config:
                    key = column['key']
                    if hasattr(obj, key):
                        value = getattr(obj, key)
                        # Manejar relaciones y métodos
                        if hasattr(value, 'id'):
                            row_data[key] = value.id
                        elif hasattr(value, '__call__'):
                            row_data[key] = value()
                        else:
                            row_data[key] = value
                    else:
                        row_data[key] = None
                data.append(row_data)
            
            return JsonResponse(data, safe=False)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Crear nuevo registro."""
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            # Validar datos requeridos
            for column in self.columns_config:
                if column.get('required', False):
                    if column['key'] not in data or not data[column['key']]:
                        return JsonResponse({
                            'error': f'El campo {column["label"]} es requerido'
                        }, status=400)
            
            # Crear objeto
            obj_data = {}
            for column in self.columns_config:
                key = column['key']
                if key in data and data[key] is not None and data[key] != '':
                    obj_data[key] = data[key]
            
            # Agregar usuario si el modelo lo requiere
            if hasattr(self.model_class, 'user'):
                obj_data['user'] = request.user
            
            obj = self.model_class.objects.create(**obj_data)
            
            # Serializar respuesta
            response_data = {'id': obj.id}
            for column in self.columns_config:
                key = column['key']
                if hasattr(obj, key):
                    value = getattr(obj, key)
                    if hasattr(value, '__call__'):
                        response_data[key] = value()
                    else:
                        response_data[key] = value
                else:
                    response_data[key] = None
            
            return JsonResponse(response_data, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# ============================================================================
# EJEMPLO 5: Configuración de URLs para tablas editables
# ============================================================================

"""
# En urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URLs para tablas editables
    path('api/tareas/', views.TareasAPIView.as_view(), name='tareas_api'),
    path('api/tareas/<int:pk>/', views.TareasAPIView.as_view(), name='tareas_api_detail'),
    
    # URLs para vistas de tabla editable
    path('tareas/', views.TareasTableView.as_view(), name='tareas_table'),
    
    # URLs para pasos con tablas editables
    path('<int:registro_id>/', views.StepsRegistroView.as_view(), name='steps'),
    path('<int:registro_id>/<str:paso_nombre>/', views.ElementoRegistroView.as_view(), name='elemento'),
]
"""

# ============================================================================
# EJEMPLO 6: Personalización de estilos CSS
# ============================================================================

"""
/* Estilos personalizados para tablas editables */
.editable-cell {
    cursor: pointer;
    position: relative;
    background-color: #f8f9fa;
    transition: background-color 0.2s ease;
}

.editable-cell:hover {
    background-color: #e9ecef;
    box-shadow: inset 0 0 0 2px #007bff;
}

.editable-cell.editing {
    background-color: #fff3cd;
    box-shadow: inset 0 0 0 2px #ffc107;
}

.editable-input {
    width: 100%;
    border: 1px solid #007bff;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 14px;
}

.editable-select {
    width: 100%;
    border: 1px solid #007bff;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 14px;
    background-color: white;
}

.table-actions {
    display: flex;
    gap: 4px;
    justify-content: center;
}

.btn-action {
    padding: 4px 8px;
    font-size: 12px;
    border-radius: 4px;
    cursor: pointer;
    border: none;
    transition: all 0.2s ease;
}

.btn-edit {
    background-color: #007bff;
    color: white;
}

.btn-edit:hover {
    background-color: #0056b3;
}

.btn-delete {
    background-color: #dc3545;
    color: white;
}

.btn-delete:hover {
    background-color: #c82333;
}

.btn-add {
    background-color: #28a745;
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    border: none;
    cursor: pointer;
    margin-bottom: 16px;
    transition: background-color 0.2s ease;
}

.btn-add:hover {
    background-color: #218838;
}
"""

# ============================================================================
# EJEMPLO 7: Validación personalizada
# ============================================================================

def validar_campo_personalizado(valor, tipo_campo, configuracion):
    """
    Función de validación personalizada para campos de tabla editable.
    """
    if tipo_campo == 'email':
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, valor):
            return False, 'Formato de email inválido'
    
    elif tipo_campo == 'telefono':
        import re
        pattern = r'^\+?[\d\s\-\(\)]+$'
        if not re.match(pattern, valor):
            return False, 'Formato de teléfono inválido'
    
    elif tipo_campo == 'numero':
        try:
            numero = float(valor)
            if 'min_value' in configuracion and numero < configuracion['min_value']:
                return False, f'El valor mínimo es {configuracion["min_value"]}'
            if 'max_value' in configuracion and numero > configuracion['max_value']:
                return False, f'El valor máximo es {configuracion["max_value"]}'
        except ValueError:
            return False, 'Debe ser un número válido'
    
    elif tipo_campo == 'texto':
        if 'max_length' in configuracion and len(valor) > configuracion['max_length']:
            return False, f'La longitud máxima es {configuracion["max_length"]} caracteres'
    
    return True, ''

# ============================================================================
# EJEMPLO 8: Integración con sistema de notificaciones
# ============================================================================

"""
// JavaScript para integración con sistema de notificaciones
function showNotification(message, type = 'info') {
    // Usar el sistema de notificaciones existente
    if (window.Alert) {
        window.Alert[type](message, { autoHide: 3000 });
    } else if (window.toastr) {
        window.toastr[type](message);
    } else {
        // Fallback a alert básico
        alert(message);
    }
}

// Ejemplo de uso en operaciones de tabla
async function saveEdit() {
    if (!tableStates.editingCell) return;
    
    try {
        // ... código de guardado ...
        
        showNotification('Campo actualizado correctamente', 'success');
    } catch (error) {
        showNotification('Error al actualizar el campo', 'error');
    }
}
"""

# ============================================================================
# RESUMEN DE USO
# ============================================================================

"""
PASOS PARA IMPLEMENTAR TABLAS EDITABLES:

1. Definir configuración de columnas:
   - Especificar campos del modelo
   - Configurar tipos de datos
   - Definir permisos de edición

2. Crear configuración de tabla:
   - Usar create_table_only_config()
   - Especificar modelo y API URL
   - Configurar permisos CRUD

3. Crear vistas API:
   - Heredar de EditableTableAPIView
   - Implementar métodos CRUD
   - Manejar permisos de usuario

4. Configurar URLs:
   - URLs para API endpoints
   - URLs para vistas de tabla

5. Personalizar estilos (opcional):
   - CSS para celdas editables
   - Estilos para botones y modales

6. Integrar en sistema de pasos:
   - Usar en PASOS_CONFIG
   - Configurar en REGISTRO_CONFIG

7. Probar funcionalidad:
   - Edición inline
   - Operaciones CRUD
   - Validaciones
   - Permisos de usuario
""" 