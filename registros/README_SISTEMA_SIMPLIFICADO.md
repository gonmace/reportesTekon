# Sistema Simplificado de Registros

## Resumen

El nuevo sistema simplificado permite crear registros de forma declarativa, eliminando la necesidad de duplicar código. Para crear un nuevo registro solo necesitas:

1. **Modelos** (heredar de `PasoBase`)
2. **Configuración declarativa** (usando `RegistroConfig` y `PasoConfig`)
3. **Vistas** (heredar de las vistas genéricas)
4. **URLs** (configuración estándar)

## Ventajas del Sistema Simplificado

### Antes (Sistema Complejo)
- ❌ Crear formularios manualmente para cada paso
- ❌ Crear clases de elementos específicas
- ❌ Crear vistas específicas para cada registro
- ❌ Duplicar código entre registros
- ❌ Mantener múltiples archivos por registro

### Ahora (Sistema Simplificado)
- ✅ Formularios generados automáticamente
- ✅ Elementos genéricos configurables
- ✅ Vistas genéricas reutilizables
- ✅ Configuración declarativa
- ✅ Un solo archivo de configuración por registro

## Cómo Crear un Nuevo Registro

### 1. Definir Modelos

```python
# models.py
from django.db import models
from registros.models.base import RegistroBase
from registros.models.paso import PasoBase

class MiRegistro(RegistroBase):
    """Modelo para mi registro."""
    class Meta:
        verbose_name = "Mi Registro"
        verbose_name_plural = "Mis Registros"

class PasoUno(PasoBase):
    """Primer paso."""
    campo_uno = models.CharField(max_length=100, verbose_name='Campo Uno')
    campo_dos = models.TextField(blank=True, null=True, verbose_name='Campo Dos')
    
    @staticmethod
    def get_etapa():
        return 'paso_uno'

class PasoDos(PasoBase):
    """Segundo paso."""
    campo_tres = models.CharField(max_length=100, verbose_name='Campo Tres')
    campo_cuatro = models.FloatField(verbose_name='Campo Cuatro')
    
    @staticmethod
    def get_etapa():
        return 'paso_dos'
```

### 2. Crear Configuración

```python
# config.py
from registros.components.registro_config import RegistroConfig, PasoConfig
from .models import MiRegistro, PasoUno, PasoDos

CONFIGURACION = RegistroConfig(
    registro_model=MiRegistro,
    pasos={
        'paso_uno': PasoConfig(
            model=PasoUno,
            fields=['campo_uno', 'campo_dos'],
            title='Paso Uno',
            description='Descripción del primer paso.',
            success_message="Datos guardados exitosamente.",
            error_message="Error al guardar los datos.",
            css_classes={
                'campo_uno': 'input input-success sombra',
                'campo_dos': 'textarea textarea-warning sombra rows-2',
            }
        ),
        'paso_dos': PasoConfig(
            model=PasoDos,
            fields=['campo_tres', 'campo_cuatro'],
            title='Paso Dos',
            description='Descripción del segundo paso.',
            widgets={
                'campo_cuatro': 'NumberInput',
            },
            css_classes={
                'campo_tres': 'input input-success sombra',
                'campo_cuatro': 'input input-success sombra',
            }
        ),
    },
    title='Mis Registros',
    breadcrumbs=[
        {'label': 'Inicio', 'url_name': 'dashboard:dashboard'},
        {'label': 'Mis Registros'}
    ]
)
```

### 3. Crear Vistas

```python
# views.py
from registros.views.generic_registro_views import (
    GenericRegistroListView, 
    GenericRegistroStepsView, 
    GenericElementoView
)
from .config import CONFIGURACION

class ListRegistrosView(GenericRegistroListView):
    def get_registro_config(self):
        return CONFIGURACION

class StepsRegistroView(GenericRegistroStepsView):
    def get_registro_config(self):
        return CONFIGURACION

class ElementoRegistroView(GenericElementoView):
    def get_registro_config(self):
        return CONFIGURACION
```

### 4. Configurar URLs

```python
# urls.py
from django.urls import path
from .views import ListRegistrosView, StepsRegistroView, ElementoRegistroView

urlpatterns = [
    path('', ListRegistrosView.as_view(), name='list'),
    path('<int:registro_id>/', StepsRegistroView.as_view(), name='steps'),
    path('<int:registro_id>/<str:paso_nombre>/', ElementoRegistroView.as_view(), name='elemento'),
]
```

## Opciones de Configuración

### PasoConfig

```python
PasoConfig(
    model=MiModelo,                    # Modelo del paso
    fields=['campo1', 'campo2'],       # Campos a incluir en el formulario
    title='Título del Paso',           # Título mostrado en la UI
    description='Descripción',         # Descripción del paso
    template_name='mi_template.html',  # Template personalizado (opcional)
    success_message='Éxito',           # Mensaje de éxito
    error_message='Error',             # Mensaje de error
    widgets={                          # Widgets personalizados
        'campo1': 'Textarea',
        'campo2': 'NumberInput',
    },
    css_classes={                      # Clases CSS personalizadas
        'campo1': 'input input-success',
        'campo2': 'textarea textarea-warning',
    }
)
```

### RegistroConfig

```python
RegistroConfig(
    registro_model=MiRegistro,         # Modelo principal del registro
    pasos={...},                       # Diccionario de pasos
    list_template='mi_lista.html',     # Template para lista (opcional)
    steps_template='mis_pasos.html',   # Template para pasos (opcional)
    title='Título del Registro',       # Título general
    breadcrumbs=[...]                  # Breadcrumbs personalizados
)
```

## Características Automáticas

El sistema genérico proporciona automáticamente:

- ✅ **Formularios dinámicos** basados en los campos del modelo
- ✅ **Validación automática** de formularios
- ✅ **Manejo de AJAX** para envíos asíncronos
- ✅ **Gestión de errores** y mensajes
- ✅ **Templates genéricos** reutilizables
- ✅ **Breadcrumbs** automáticos
- ✅ **Estadísticas** de registros
- ✅ **Completitud** de pasos
- ✅ **Sub-elementos** (fotos, mapas, etc.)

## Migración del Sistema Actual

Para migrar registros existentes al nuevo sistema:

1. **Mantener modelos** existentes
2. **Crear configuración** declarativa
3. **Reemplazar vistas** con las genéricas
4. **Actualizar URLs** si es necesario
5. **Eliminar archivos** obsoletos (formularios, elementos específicos)

## Ejemplo Completo

Ver `registros/ejemplo_nuevo_registro.py` para un ejemplo completo de implementación.

## Beneficios

- **Reducción de código**: 90% menos código para nuevos registros
- **Mantenimiento fácil**: Cambios centralizados en la configuración
- **Consistencia**: Todos los registros funcionan igual
- **Extensibilidad**: Fácil agregar nuevas características
- **Testing**: Menos código = menos bugs
- **Documentación**: Configuración autodocumentada

¡El sistema simplificado hace que crear nuevos registros sea súper fácil y rápido! 