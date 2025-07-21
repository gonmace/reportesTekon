# Template Genérico de Registros

Este template genérico permite reutilizar la funcionalidad de listado de registros en diferentes aplicaciones de Django.

## Ubicación

- `registros/templates/components/generic_registros_template.html`: Template base con JavaScript embebido

## Cómo Usar en Otra Aplicación

### 1. Crear el Template Específico

```html
<!-- mi_app/templates/pages/main_mi_app.html -->
{% extends 'registros/components/generic_registros_template.html' %}
```

### 2. Configurar la Vista

```python
# mi_app/views.py
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
import json

class MiAppListView(LoginRequiredMixin, ListView):
    template_name = 'pages/main_mi_app.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Configuración específica para tu aplicación
        context.update({
            'page_title': 'Mi Aplicación',
            'show_activate_button': True,
            'activate_button_text': 'Crear Registro',
            'api_base_url': self.request.build_absolute_uri('/mi_app/api/v1/'),
            'registros_url': self.request.build_absolute_uri('/mi_app/api/v1/registros/'),
            'usuarios_url': self.request.build_absolute_uri('/mi_app/api/v1/usuarios/'),
            'activar_url': self.request.build_absolute_uri('/mi_app/activar/'),
            'table_id': '#registros-table',
            'page_length': 10,
            'show_actions': self.request.user.is_superuser,
            'actions_url': self.request.build_absolute_uri('/mi_app/registros/'),
            'modal_id': '#activar-registro-modal',
            'activar_btn_id': '#activar-registro-btn',
            'modal_template': 'components/mi_app_activar_form.html',
            
            # Configuración de columnas
            'table_columns': [
                {'title': 'ID', 'center': True},
                {'title': 'Nombre', 'center': True},
                {'title': 'Descripción'},
            ],
            'table_columns_json': json.dumps([
                {'data': 'id', 'className': '!text-center', 'title': 'ID'},
                {'data': 'nombre', 'className': '!text-center', 'title': 'Nombre'},
                {'data': 'descripcion', 'className': 'w-fit max-w-40', 'title': 'Descripción'},
            ])
        })
        
        # Agregar columnas adicionales para superusuarios
        if self.request.user.is_superuser:
            context['table_columns'].extend([
                {'title': 'Usuario', 'center': True, 'nowrap': True},
                {'title': 'Acciones', 'center': True, 'nowrap': True},
            ])
            context['table_columns_json'] = json.dumps([
                {'data': 'id', 'className': '!text-center', 'title': 'ID'},
                {'data': 'nombre', 'className': '!text-center', 'title': 'Nombre'},
                {'data': 'descripcion', 'className': 'w-fit max-w-40', 'title': 'Descripción'},
                {'data': 'user.username', 'className': '!text-center', 'width': '150px', 'title': 'Usuario', 'editable': True},
                {'data': None, 'orderable': False, 'className': 'text-center', 'title': 'Acciones'},
            ])
        
        return context
```

### 3. Configurar URLs

```python
# mi_app/urls.py
from django.urls import path
from .views import MiAppListView

urlpatterns = [
    path('', MiAppListView.as_view(), name='list'),
    path('api/v1/registros/', MiAppRegistrosAPIView.as_view(), name='api_registros'),
    path('api/v1/usuarios/', MiAppUsuariosAPIView.as_view(), name='api_usuarios'),
    path('activar/', MiAppActivarView.as_view(), name='activar'),
]
```

### 4. Crear el Modal de Activación (Opcional)

```html
<!-- mi_app/templates/components/mi_app_activar_form.html -->
<dialog id="activar-registro-modal" class="modal">
    <div class="modal-box">
        <h3 class="font-bold text-lg">Crear Nuevo Registro</h3>
        <form method="post" action="{% url 'mi_app:activar' %}">
            {% csrf_token %}
            <div class="form-control">
                <label class="label">
                    <span class="label-text">Campo 1</span>
                </label>
                <input type="text" name="campo1" class="input input-bordered" required />
            </div>
            <div class="form-control">
                <label class="label">
                    <span class="label-text">Campo 2</span>
                </label>
                <input type="text" name="campo2" class="input input-bordered" required />
            </div>
            <div class="modal-action">
                <button type="button" class="btn" onclick="closeModal()">Cancelar</button>
                <button type="submit" class="btn btn-primary">Crear</button>
            </div>
        </form>
    </div>
</dialog>
```

## Parámetros de Configuración

### Parámetros Básicos

- `page_title`: Título de la página
- `show_activate_button`: Mostrar/ocultar botón de activación
- `activate_button_text`: Texto del botón de activación
- `api_base_url`: URL base de la API
- `registros_url`: URL para obtener registros
- `usuarios_url`: URL para obtener usuarios
- `activar_url`: URL para activar registros
- `table_id`: ID de la tabla
- `page_length`: Número de registros por página
- `show_actions`: Mostrar/ocultar columna de acciones
- `actions_url`: URL base para acciones
- `modal_id`: ID del modal
- `activar_btn_id`: ID del botón de activación
- `modal_template`: Template del modal

### Configuración de Columnas

- `table_columns`: Lista de columnas para el HTML
- `table_columns_json`: Configuración JSON para DataTables

### Propiedades de Columnas

- `title`: Título de la columna
- `center`: Centrar contenido
- `nowrap`: Evitar salto de línea
- `class_name`: Clases CSS adicionales
- `data`: Campo de datos para DataTables
- `className`: Clases CSS para DataTables
- `width`: Ancho de la columna
- `editable`: Si la columna es editable
- `orderable`: Si la columna es ordenable

## Funcionalidades Incluidas

- Tabla con DataTables
- Búsqueda personalizada
- Paginación
- Edición inline de campos (para superusuarios)
- Modal de activación
- Manejo de errores
- Notificaciones con Alert component
- Responsive design

## Personalización

El template es completamente configurable a través de los parámetros del contexto. Puedes:

- Cambiar las columnas de la tabla
- Modificar las URLs de la API
- Personalizar el modal de activación
- Ajustar el comportamiento según el tipo de usuario
- Agregar funcionalidades específicas extendiendo las clases JavaScript

## Ejemplo de Uso en TX/TSS

```html
<!-- registros_txtss/templates/pages/main_txtss.html -->
{% extends 'registros/components/generic_registros_template.html' %}
```

```python
# registros_txtss/views.py
class ListRegistrosView(GenericRegistroListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'page_title': 'TX/TSS',
            'show_activate_button': True,
            'activate_button_text': 'Activar Registro',
            'api_base_url': self.request.build_absolute_uri('/txtss/api/v1/'),
            'registros_url': self.request.build_absolute_uri('/txtss/api/v1/registros/'),
            'usuarios_url': self.request.build_absolute_uri('/txtss/api/v1/usuarios/usuarios_ito/'),
            'activar_url': self.request.build_absolute_uri('/txtss/activar/'),
            'table_id': '#registros-table',
            'page_length': 10,
            'show_actions': self.request.user.is_superuser,
            'actions_url': self.request.build_absolute_uri('/txtss/registros/'),
            'modal_id': '#activar-registro-modal',
            'activar_btn_id': '#activar-registro-btn',
            'modal_template': 'components/activar_registro_form.html',
            
            'table_columns': [
                {'title': 'PTI ID', 'center': True},
                {'title': 'Operador ID', 'center': True},
                {'title': 'Nombre Sitio'},
            ],
            'table_columns_json': json.dumps([
                {'data': 'sitio.pti_cell_id', 'className': '!text-center', 'title': 'PTI ID'},
                {'data': 'sitio.operator_id', 'className': '!text-center', 'title': 'Operador ID'},
                {'data': 'sitio.name', 'className': 'w-fit max-w-40', 'title': 'Nombre Sitio'},
            ])
        })
        
        if self.request.user.is_superuser:
            context['table_columns'].extend([
                {'title': 'ITO', 'center': True, 'nowrap': True},
                {'title': 'Registro', 'center': True, 'nowrap': True},
            ])
            context['table_columns_json'] = json.dumps([
                {'data': 'sitio.pti_cell_id', 'className': '!text-center', 'title': 'PTI ID'},
                {'data': 'sitio.operator_id', 'className': '!text-center', 'title': 'Operador ID'},
                {'data': 'sitio.name', 'className': 'w-fit max-w-40', 'title': 'Nombre Sitio'},
                {'data': 'user.username', 'className': '!text-center', 'width': '150px', 'title': 'ITO', 'editable': True},
                {'data': None, 'orderable': False, 'className': 'text-center', 'title': 'Registro'},
            ])
        
        return context
``` 