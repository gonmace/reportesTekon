# Sistema de Registros - Aplicación Base

Esta es la aplicación base que proporciona las clases y funcionalidades comunes para crear aplicaciones de registros específicas.

## Arquitectura

### Clases Base

1. **`RegistroBase`** - Modelo base para registros
2. **`PasoBase`** - Modelo base para pasos
3. **`ElementoBase`** - Clase base para elementos
4. **`RegistroListView`** - Vista base para listar registros
5. **`RegistroStepsView`** - Vista base para mostrar pasos
6. **`ElementoView`** - Vista base para manejar elementos

## Cómo Crear una Nueva Aplicación de Registros

### 1. Crear la aplicación

```bash
python manage.py startapp mi_registro
```

### 2. Crear el modelo principal

```python
# mi_registro/models.py
from registros.models.base import RegistroBase

class Registros(RegistroBase):
    """Modelo para mi tipo de registro."""
    class Meta:
        verbose_name = "Mi Registro"
        verbose_name_plural = "Mis Registros"
```

### 3. Crear los pasos

```python
# mi_registro/models.py
from registros.models.paso import PasoBase
from django.db import models

class Paso1(PasoBase):
    """Primer paso."""
    campo1 = models.CharField(max_length=100)
    campo2 = models.TextField()
    
    @staticmethod
    def get_etapa():
        return 'paso1'

class Paso2(PasoBase):
    """Segundo paso."""
    campo3 = models.CharField(max_length=100)
    
    @staticmethod
    def get_etapa():
        return 'paso2'
```

### 4. Crear los formularios

```python
# mi_registro/forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from .models import Paso1, Paso2

class Paso1Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('campo1'),
            Field('campo2'),
            Submit('submit', 'Guardar'),
        )
    
    class Meta:
        model = Paso1
        fields = ['campo1', 'campo2']

class Paso2Form(forms.ModelForm):
    # Similar a Paso1Form
    pass
```

### 5. Crear los elementos

```python
# mi_registro/elementos.py
from registros.elementos.base import ElementoBase
from .models import Paso1, Paso2
from .forms import Paso1Form, Paso2Form

class ElementoPaso1(ElementoBase):
    model = Paso1
    form_class = Paso1Form
    tipo = 'paso1'
    template_name = 'registros/elemento_form.html'
    success_message = "Paso 1 guardado exitosamente."
    error_message = "Error al guardar el paso 1."

class ElementoPaso2(ElementoBase):
    model = Paso2
    form_class = Paso2Form
    tipo = 'paso2'
    template_name = 'registros/elemento_form.html'
    success_message = "Paso 2 guardado exitosamente."
    error_message = "Error al guardar el paso 2."
```

### 6. Crear las vistas

```python
# mi_registro/views.py
from registros.views.base import RegistroListView, RegistroStepsView, ElementoView
from .models import Registros
from .elementos import ElementoPaso1, ElementoPaso2
from typing import Dict, Any

class ListRegistrosView(RegistroListView):
    model = Registros
    
    class Meta:
        title = 'Mis Registros'
        header_title = 'Mis Registros'
        breadcrumbs = [
            {'label': 'Inicio', 'url_name': 'dashboard:dashboard'},
            {'label': 'Mis Registros'}
        ]

class StepsRegistroView(RegistroStepsView):
    model = Registros
    template_name = 'mi_registro/steps.html'
    
    def get_steps_config(self) -> Dict[str, Dict[str, Any]]:
        return {
            'paso1': {
                'elemento_class': ElementoPaso1,
                'title': 'Paso 1',
                'description': 'Descripción del paso 1.',
            },
            'paso2': {
                'elemento_class': ElementoPaso2,
                'title': 'Paso 2',
                'description': 'Descripción del paso 2.',
            },
        }

class ElementoRegistroView(ElementoView):
    model = Registros
    
    def get_elemento_class(self, paso_nombre):
        elementos_map = {
            'paso1': ElementoPaso1,
            'paso2': ElementoPaso2,
        }
        return elementos_map.get(paso_nombre)
```

### 7. Crear las URLs

```python
# mi_registro/urls.py
from django.urls import path
from .views import ListRegistrosView, StepsRegistroView, ElementoRegistroView

app_name = "mi_registro"

urlpatterns = [
    path("", ListRegistrosView.as_view(), name="list"),
    path("<int:registro_id>/", StepsRegistroView.as_view(), name="steps"),
    path("<int:registro_id>/paso/<str:paso_nombre>/", ElementoRegistroView.as_view(), name="elemento"),
]
```

### 8. Registrar en settings.py

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'mi_registro',
]
```

### 9. Incluir en URLs principales

```python
# config/urls.py
urlpatterns = [
    # ...
    path('mi-registro/', include('mi_registro.urls')),
]
```

## Ventajas de esta Arquitectura

1. **Simplicidad**: Solo necesitas crear algunos archivos
2. **Reutilización**: Todas las funcionalidades base están en `registros`
3. **Consistencia**: Todas las aplicaciones funcionan igual
4. **Flexibilidad**: Puedes personalizar cada paso según necesites
5. **Mantenibilidad**: Cambios en la base se reflejan en todas las aplicaciones

## URLs Generadas

- **Lista**: `/mi-registro/`
- **Pasos**: `/mi-registro/{id}/`
- **Elemento**: `/mi-registro/{id}/paso/{paso_nombre}/`

## Próximos Pasos

1. Crear templates específicos si es necesario
2. Agregar validaciones personalizadas
3. Implementar sub-elementos (fotos, mapas, etc.)
4. Agregar lógica de negocio específica 