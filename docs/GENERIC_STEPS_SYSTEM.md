# Sistema de Steps Genérico

## Descripción General

El nuevo sistema de steps genérico permite configurar cada paso con cualquier combinación de elementos (formulario, fotos, mapas, desfase) de manera completamente declarativa. Esto elimina la necesidad de crear templates específicos para cada combinación de elementos.

## Características Principales

- ✅ **Configuración declarativa**: Cada step se define con una configuración JSON
- ✅ **Elementos opcionales**: Fotos, mapas y desfase son completamente opcionales
- ✅ **Múltiples mapas**: Soporte para hasta 9 coordenadas por mapa
- ✅ **Orden personalizable**: Los steps se pueden ordenar según necesidades
- ✅ **Títulos y descripciones**: Cada step puede tener título y descripción personalizados
- ✅ **Fotos requeridas**: Las fotos pueden ser marcadas como obligatorias
- ✅ **Un solo template**: Todo se maneja con un template genérico

## Configuración de Steps

### Estructura Básica

```python
def get_steps_config(self) -> Dict[str, Dict[str, Any]]:
    return {
        'step_name': {
            'model_class': ModelClass,
            'elements': {
                'photos': { ... },  # Opcional
                'map': { ... },     # Opcional
                'desfase': { ... }  # Opcional
            },
            'order': int,           # Opcional
            'title': str,           # Opcional
            'description': str      # Opcional
        }
    }
```

### Configuración de Elementos

#### Formulario (Siempre presente)
El formulario siempre está presente en todos los steps, no requiere configuración.

#### Fotos
```python
'photos': {
    'enabled': True,        # Habilitar fotos
    'min_count': 4,         # Mínimo de fotos requeridas
    'required': False       # Si las fotos son obligatorias
}
```

#### Mapa
```python
'map': {
    'enabled': True,
    'coordinates': {
        'coordinates_1': {
            'model': 'site',      # 'site', 'current', o nombre del modelo
            'lat': 'lat_base',    # Campo de latitud
            'lon': 'lon_base',    # Campo de longitud
            'label': 'Mandato',   # Etiqueta para mostrar
            'color': '#3B82F6',   # Color del marcador
            'size': 'large'       # Tamaño: 'small', 'mid', 'large', 'xlarge'
        },
        'coordinates_2': { ... },  # Más coordenadas hasta coordinates_9
    }
}
```

#### Desfase
```python
'desfase': {
    'enabled': True,
    'reference': 'site',  # Usar sitio base como referencia
    'description': 'Distancia desde el mandato'  # Descripción opcional del desfase
}
```

## Ejemplos de Configuración

### Step con Solo Formulario
```python
'simple_step': {
    'model_class': SimpleModel,
    'elements': {
        # No se especifican elementos adicionales
    },
    'order': 1,
    'title': 'Información Básica',
    'description': 'Datos generales del registro'
}
```

### Step con Formulario y Fotos
```python
'photo_step': {
    'model_class': PhotoModel,
    'elements': {
        'photos': {
            'enabled': True,
            'min_count': 3,
            'required': True
        }
    },
    'order': 2,
    'title': 'Documentación',
    'description': 'Fotos del sitio'
}
```

### Step con Formulario y Mapa
```python
'map_step': {
    'model_class': MapModel,
    'elements': {
        'map': {
            'enabled': True,
            'coordinates': {
                'coordinates_1': {
                    'model': 'current',
                    'lat': 'lat',
                    'lon': 'lon',
                    'label': 'Ubicación',
                    'color': '#8B5CF6',
                    'size': 'large'
                }
            }
        }
    },
    'order': 3,
    'title': 'Ubicación',
    'description': 'Coordenadas del punto'
}
```

### Step Completo (Formulario + Fotos + Mapa + Desfase)
```python
'complete_step': {
    'model_class': CompleteModel,
    'elements': {
        'photos': {
            'enabled': True,
            'min_count': 4,
            'required': False
        },
        'map': {
            'enabled': True,
            'coordinates': {
                'coordinates_1': {
                    'model': 'site',
                    'lat': 'lat_base',
                    'lon': 'lon_base',
                    'label': 'Mandato',
                    'color': '#3B82F6',
                    'size': 'large'
                },
                'coordinates_2': {
                    'model': 'current',
                    'lat': 'lat',
                    'lon': 'lon',
                    'label': 'Inspección',
                    'color': '#F59E0B',
                    'size': 'mid'
                }
            }
        },
        'desfase': {
            'enabled': True,
            'reference': 'site',
            'description': 'Distancia desde el mandato'
        }
    },
    'order': 1,
    'title': 'Sitio',
    'description': 'Información general del sitio'
}
```

## Configuración Actual (StepsRegistroView)

La configuración actual incluye tres steps:

### 1. Sitio
- ✅ Formulario
- ✅ Fotos (4 mínimas)
- ✅ Mapa (2 coordenadas: Mandato + Inspección)
- ✅ Desfase
- Orden: 1

### 2. Acceso
- ✅ Formulario
- ✅ Fotos (4 mínimas)
- ✅ Mapa (1 coordenada: Acceso)
- ✅ Desfase
- Orden: 2

### 3. Empalme
- ✅ Formulario
- ✅ Fotos (3 mínimas)
- ✅ Mapa (3 coordenadas: Sitio + Empalme + Mandato)
- ✅ Desfase
- Orden: 3

## Cómo Agregar un Nuevo Step

### 1. Crear el Modelo
```python
# registrostxtss/nuevo_step/models.py
from django.db import models
from core.models import BaseModel
from registrostxtss.models.registrostxtss import RegistrosTxTss

class NuevoStep(BaseModel):
    registro = models.ForeignKey(RegistrosTxTss, on_delete=models.CASCADE)
    # ... otros campos
    
    @staticmethod
    def get_etapa():
        return 'nuevo_step'
    
    @staticmethod
    def check_completeness(nuevo_step_id):
        return check_model_completeness(NuevoStep, nuevo_step_id)
```

### 2. Crear el Formulario
```python
# registrostxtss/nuevo_step/form.py
from django import forms
from .models import NuevoStep

class NuevoStepForm(forms.ModelForm):
    class Meta:
        model = NuevoStep
        fields = ['registro', 'campo1', 'campo2']
```

### 3. Crear la Vista
```python
# registrostxtss/nuevo_step/views.py
from registrostxtss.views.generic_views import GenericRegistroView
from .models import NuevoStep
from .form import NuevoStepForm

class NuevoStepView(GenericRegistroView):
    form_class = NuevoStepForm
    
    def setup(self, request, *args, **kwargs):
        kwargs['model_class'] = NuevoStep
        kwargs['etapa'] = 'nuevo_step'
        super().setup(request, *args, **kwargs)
```

### 4. Agregar URL
```python
# registrostxtss/urls.py
from .nuevo_step.views import NuevoStepView

urlpatterns = [
    # ... otras URLs
    path("registrostxtss/<int:registro_id>/nuevo_step/", NuevoStepView.as_view(), name="r_nuevo_step"),
]
```

### 5. Configurar en StepsRegistroView
```python
# registrostxtss/views/base_steps_view.py
def get_steps_config(self):
    from registrostxtss.nuevo_step.models import NuevoStep
    
    return {
        # ... steps existentes
        'nuevo_step': {
            'model_class': NuevoStep,
            'elements': {
                'form': True,
                'photos': {
                    'enabled': True,
                    'min_count': 2,
                    'required': False
                },
                'map': {
                    'enabled': True,
                    'coordinates': {
                        'coordinates_1': {
                            'model': 'current',
                            'lat': 'lat',
                            'lon': 'lon',
                            'label': 'Nuevo Punto',
                            'color': '#10B981',
                            'size': 'large'
                        }
                    }
                }
            },
            'order': 4,
            'title': 'Nuevo Step',
            'description': 'Descripción del nuevo step'
        }
    }
```

## Ventajas del Sistema Genérico

1. **Flexibilidad**: Cualquier combinación de elementos es posible
2. **Mantenibilidad**: Un solo template para manejar todos los casos
3. **Escalabilidad**: Agregar nuevos steps es muy simple
4. **Consistencia**: Todos los steps tienen el mismo comportamiento base
5. **Configuración**: Todo se define de manera declarativa
6. **Reutilización**: La lógica común está centralizada

## Migración desde el Sistema Anterior

El sistema anterior requería:
- `step.html` para steps básicos
- `step&photo&map.html` para steps con fotos y mapas
- Configuración manual en el template

El nuevo sistema requiere:
- `step_generic.html` para todos los steps
- Configuración en `get_steps_config()`
- El template se genera automáticamente

## Compatibilidad

El nuevo sistema es completamente compatible con el anterior. Los templates antiguos siguen funcionando si se necesitan casos especiales. 