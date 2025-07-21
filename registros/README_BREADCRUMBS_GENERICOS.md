# Sistema de Breadcrumbs Genéricos para Registros

Este documento explica cómo usar el nuevo sistema de breadcrumbs genéricos que centraliza la lógica de navegación para todas las vistas de registro.

## Arquitectura

### 1. Funciones Utilitarias (`registros/utils/breadcrumbs.py`)

```python
from registros.utils.breadcrumbs import generate_registro_breadcrumbs, resolve_breadcrumbs, get_sitio_codigo

# Generar breadcrumbs completos
breadcrumbs = generate_registro_breadcrumbs(
    registro_id=1,
    paso_nombre='sitio',
    registro_model=Registros,
    registro_config=REGISTRO_CONFIG
)
```

### 2. Mixin Genérico (`registros/mixins/breadcrumbs_mixin.py`)

```python
from registros.mixins.breadcrumbs_mixin import RegistroBreadcrumbsMixin

class MiVistaView(RegistroBreadcrumbsMixin, TemplateView):
    def get_registro_config(self):
        return MI_CONFIG
```

## Uso Automático

### Para Vistas de Pasos

```python
class StepsRegistroView(GenericRegistroStepsView):
    """Vista para mostrar los pasos de un registro."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG
    # ¡No necesitas definir get_breadcrumbs()!
```

### Para Vistas de Elementos

```python
class ElementoRegistroView(GenericElementoView):
    """Vista para manejar elementos de registro."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG
    # ¡No necesitas definir get_breadcrumbs()!
```

## Breadcrumbs Generados

### Página de Pasos (`/txtss/registros/1/`)
```
Inicio > Registros TX/TSS > CL-AN-1284
```

### Página de Elemento (`/txtss/registros/1/sitio/`)
```
Inicio > Registros TX/TSS > CL-AN-1284 > Sitio
```

### Página de Elemento (`/txtss/registros/1/acceso/`)
```
Inicio > Registros TX/TSS > CL-AN-1284 > Acceso
```

## Ventajas del Sistema Genérico

✅ **Sin duplicación de código**: Una sola función maneja todos los breadcrumbs  
✅ **Mantenimiento fácil**: Cambios en un lugar se reflejan en todas las vistas  
✅ **Consistencia**: Todas las vistas tienen el mismo comportamiento  
✅ **Flexibilidad**: Fácil de personalizar para casos específicos  
✅ **Reutilización**: Funciona para cualquier tipo de registro  
✅ **Verdaderamente genérico**: Funciona con cualquier aplicación de registros  

## Personalización

### Para Casos Específicos

Si necesitas personalizar los breadcrumbs para una vista específica:

```python
class MiVistaEspecialView(RegistroBreadcrumbsMixin, TemplateView):
    def get_breadcrumbs(self):
        # Obtener breadcrumbs base
        breadcrumbs = super().get_breadcrumbs()
        
        # Agregar breadcrumb personalizado
        breadcrumbs.append({'label': 'Mi Sección Especial'})
        
        return breadcrumbs
```

### Para Diferentes Tipos de Registro

```python
def generate_registro_breadcrumbs(registro_id, paso_nombre=None, registro_model=None, registro_config=None):
    # La función ya maneja diferentes tipos de registro automáticamente
    # basándose en registro_config.title y app_namespace
```

## Migración desde el Sistema Anterior

### Antes (código duplicado):
```python
class StepsRegistroView(GenericRegistroStepsView):
    def get_breadcrumbs(self):
        breadcrumbs = [
            {'label': 'Inicio', 'url_name': 'dashboard:dashboard'},
            {'label': 'Registros TX/TSS', 'url_name': 'registros_txtss:list'}
        ]
        # ... 30 líneas de código duplicado ...
        return self._resolve_breadcrumbs(breadcrumbs)
```

### Ahora (genérico):
```python
class StepsRegistroView(GenericRegistroStepsView):
    def get_registro_config(self):
        return REGISTRO_CONFIG
    # ¡Eso es todo!
```

## Funciones Disponibles

### `generate_registro_breadcrumbs()`
Genera breadcrumbs completos para cualquier vista de registro.

**Parámetros:**
- `registro_id`: ID del registro
- `paso_nombre`: Nombre del paso actual (opcional)
- `registro_model`: Modelo del registro
- `registro_config`: Configuración del registro

### `resolve_breadcrumbs()`
Resuelve las URLs de una lista de breadcrumbs.

### `get_sitio_codigo()`
Obtiene el código del sitio de un registro (pti_cell_id o operator_id).

### `get_app_namespace_from_config()`
Determina el namespace de la aplicación basándose en la configuración.

## Ejemplos de Uso

### Crear Nueva Aplicación de Registro: registros_obra

```python
# registros_obra/config.py
from registros.components.registro_config import RegistroConfig, PasoConfig, ElementoConfig
from .models import RegistrosObra, RSitioObra, RAccesoObra

PASOS_CONFIG = {
    'sitio': PasoConfig(
        elemento=ElementoConfig(
            nombre='sitio',
            model=RSitioObra,
            fields=['nombre_obra', 'ubicacion', 'comentarios'],
            title='Sitio de Obra',
            description='Información general del sitio de obra.',
        ),
        title='Sitio de Obra',
        description='Información general del sitio de obra.'
    ),
    'acceso': PasoConfig(
        elemento=ElementoConfig(
            nombre='acceso',
            model=RAccesoObra,
            fields=['tipo_acceso', 'distancia', 'comentarios'],
            title='Acceso a Obra',
            description='Información sobre el acceso al sitio de obra.',
        ),
        title='Acceso a Obra',
        description='Información sobre el acceso al sitio de obra.'
    ),
}

REGISTRO_CONFIG = RegistroConfig(
    registro_model=RegistrosObra,
    pasos=PASOS_CONFIG,
    list_template='pages/main_obra.html',
    steps_template='pages/steps_obra.html',
    title='Registros de Obra',
    app_namespace='registros_obra',  # ¡Namespace específico!
)

# registros_obra/views.py
from registros.views.generic_registro_views import GenericRegistroListView, GenericRegistroStepsView, GenericElementoView
from .config import REGISTRO_CONFIG

class ListRegistrosObraView(GenericRegistroListView):
    def get_registro_config(self):
        return REGISTRO_CONFIG

class StepsRegistroObraView(GenericRegistroStepsView):
    def get_registro_config(self):
        return REGISTRO_CONFIG

class ElementoRegistroObraView(GenericElementoView):
    def get_registro_config(self):
        return REGISTRO_CONFIG

# registros_obra/urls.py
from django.urls import path
from .views import ListRegistrosObraView, StepsRegistroObraView, ElementoRegistroObraView

app_name = 'registros_obra'

urlpatterns = [
    path('', ListRegistrosObraView.as_view(), name='list'),
    path('<int:registro_id>/', StepsRegistroObraView.as_view(), name='steps'),
    path('<int:registro_id>/<str:paso_nombre>/', ElementoRegistroObraView.as_view(), name='elemento'),
]
```

### URLs y Breadcrumbs Generados Automáticamente:

```
/obra/registros/1/ -> Inicio > Registros de Obra > CL-AN-1284
/obra/registros/1/sitio/ -> Inicio > Registros de Obra > CL-AN-1284 > Sitio de Obra
/obra/registros/1/acceso/ -> Inicio > Registros de Obra > CL-AN-1284 > Acceso a Obra
```

### Crear Nueva Aplicación: registros_test

```python
# registros_test/config.py
REGISTRO_CONFIG = RegistroConfig(
    registro_model=RegistrosTest,
    pasos=PASOS_CONFIG,
    title='Registros de Test',
    app_namespace='registros_test',  # Namespace específico
)

# URLs generadas automáticamente:
# /test/registros/1/ -> Inicio > Registros de Test > CL-AN-1284
# /test/registros/1/paso1/ -> Inicio > Registros de Test > CL-AN-1284 > Paso 1
```

## Determinación Automática del Namespace

El sistema determina el namespace de la aplicación en este orden:

1. **Configuración explícita**: `app_namespace` en `RegistroConfig`
2. **Mapeo por app_label**: Basado en el modelo del registro
3. **Fallback por título**: Basado en palabras clave en el título
4. **Fallback por defecto**: `registros_txtss`

### Mapeo de app_label a namespace:
```python
namespace_mapping = {
    'registros_txtss': 'registros_txtss',
    'registros_obra': 'registros_obra',
    'registros_test': 'registros_test',
    # Agregar más según sea necesario
}
``` 