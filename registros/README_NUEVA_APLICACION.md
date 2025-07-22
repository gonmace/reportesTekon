# Crear una Nueva Aplicación de Registros

Este documento explica cómo crear una nueva aplicación de registros usando el sistema genérico de `registros`.

## 1. Crear la Aplicación

```bash
python manage.py startapp mi_nueva_app
```

## 2. Agregar la Aplicación a INSTALLED_APPS

En `config/base.py`:

```python
INSTALLED_APPS = [
    # ... otras apps ...
    'mi_nueva_app',
]
```

## 3. Crear los Modelos

En `mi_nueva_app/models.py`:

```python
from registros.models.base import RegistroBase
from registros.models.paso import PasoBase
from django.db import models
from registros.models.validators import validar_latitud, validar_longitud
from registros.models.completeness_checker import check_model_completeness
from core.models.sites import Site
from users.models import User
from simple_history.models import HistoricalRecords

class MiRegistro(RegistroBase):
    """Modelo principal para mi nueva aplicación."""
    title = models.CharField(max_length=100, verbose_name='Título')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Registro {self.id}"

# Paso específico con mapa
class RSitio(PasoBase):
    """Paso Sitio con coordenadas."""
    registro = models.ForeignKey(MiRegistro, on_delete=models.CASCADE, verbose_name='Registro')
    lat = models.FloatField(validators=[validar_latitud], verbose_name='Latitud')
    lon = models.FloatField(validators=[validar_longitud], verbose_name='Longitud')
    dimensiones = models.CharField(max_length=100, verbose_name='Dimensiones')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Sitio'
        verbose_name_plural = 'Registros Sitio'
    
    @staticmethod
    def get_etapa():
        return 'sitio'
    
    @staticmethod
    def get_actives():
        return RSitio.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(rsitio_id):
        return check_model_completeness(RSitio, rsitio_id)

# Paso simple
class RDatos(PasoBase):
    """Paso con datos simples."""
    registro = models.ForeignKey(MiRegistro, on_delete=models.CASCADE, verbose_name='Registro')
    campo1 = models.CharField(max_length=100, verbose_name='Campo 1')
    campo2 = models.CharField(max_length=100, verbose_name='Campo 2')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Datos'
        verbose_name_plural = 'Registros Datos'
    
    @staticmethod
    def get_etapa():
        return 'datos'
    
    @staticmethod
    def get_actives():
        return RDatos.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(rdatos_id):
        return check_model_completeness(RDatos, rdatos_id)
```

## 4. Crear los Formularios

En `mi_nueva_app/forms.py`:

```python
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from .models import RSitio, RDatos, MiRegistro

class RSitioForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.registro_id = kwargs.pop('registro_id', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'pb-4'
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        # Configurar el campo registro
        if self.registro_id:
            registro_obj = MiRegistro.objects.get(id=self.registro_id)
            self.initial['registro'] = registro_obj.id
            self.fields['registro'].widget = forms.HiddenInput()
        
        # Layout específico para sitio con mapa
        self.helper.layout = Layout(
            Field('registro'),
            # Aquí puedes agregar el layout específico para mapa
            Field('lat', css_class='input input-success sombra'),
            Field('lon', css_class='input input-success sombra'),
            Field('dimensiones', css_class='input input-success sombra'),
            Field('comentarios', css_class='textarea textarea-warning sombra rows-2'),
            Submit('submit', 'Guardar', css_class='btn btn-primary'),
        )
    
    class Meta:
        model = RSitio
        fields = ['registro', 'lat', 'lon', 'dimensiones', 'comentarios']

class RDatosForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.registro_id = kwargs.pop('registro_id', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'pb-4'
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        # Configurar el campo registro
        if self.registro_id:
            registro_obj = MiRegistro.objects.get(id=self.registro_id)
            self.initial['registro'] = registro_obj.id
            self.fields['registro'].widget = forms.HiddenInput()
        
        self.helper.layout = Layout(
            Field('registro'),
            Field('campo1', css_class='input input-success sombra'),
            Field('campo2', css_class='input input-success sombra'),
            Field('comentarios', css_class='textarea textarea-warning sombra rows-2'),
            Submit('submit', 'Guardar', css_class='btn btn-primary'),
        )
    
    class Meta:
        model = RDatos
        fields = ['registro', 'campo1', 'campo2', 'comentarios']
```

## 5. Crear la Configuración

En `mi_nueva_app/config.py`:

```python
from registros.config import create_photo_map_config, create_photo_config, create_simple_config, create_registro_config
from .models import MiRegistro, RSitio, RDatos
from .forms import RSitioForm, RDatosForm

# Configuración de pasos
PASOS_CONFIG = {
    'sitio': create_photo_map_config(
        model_class=RSitio,
        form_class=RSitioForm,
        title='Sitio',
        description='Información general del sitio.'
    ),
    'datos': create_photo_config(
        model_class=RDatos,
        form_class=RDatosForm,
        fields=['campo1', 'campo2', 'comentarios'],
        title='Datos',
        description='Información adicional.',
        photo_count=3
    ),
}

# Configuración completa del registro
REGISTRO_CONFIG = create_registro_config(
    registro_model=MiRegistro,
    pasos_config=PASOS_CONFIG,
    title='Mi Nueva App',
    app_namespace='mi_nueva_app',
    list_template='pages/main_mi_app.html',
    steps_template='pages/steps_mi_app.html'
)
```

## 6. Crear las Vistas

En `mi_nueva_app/views.py`:

```python
from registros.views.generic_registro_views import (
    GenericRegistroTableListView, 
    GenericRegistroStepsView, 
    GenericElementoView
)
from registros.views.generic_views import GenericActivarRegistroView
from .config import REGISTRO_CONFIG

class ListRegistrosView(GenericRegistroTableListView):
    """Vista para listar registros."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG

class StepsRegistroView(GenericRegistroStepsView):
    """Vista para mostrar los pasos de un registro."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG

class ElementoRegistroView(GenericElementoView):
    """Vista para manejar elementos de registro."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG

class ActivarRegistroView(GenericActivarRegistroView):
    """Vista para activar registros."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG
```

## 7. Crear las URLs

En `mi_nueva_app/urls.py`:

```python
from django.urls import path
from .views import (
    ListRegistrosView,
    StepsRegistroView, 
    ElementoRegistroView,
    ActivarRegistroView
)

app_name = 'mi_nueva_app'

urlpatterns = [
    path('', ListRegistrosView.as_view(), name='list'),
    path('activar/', ActivarRegistroView.as_view(), name='activar'),
    path('<int:registro_id>/', StepsRegistroView.as_view(), name='steps'),
    path('<int:registro_id>/<str:paso_nombre>/', ElementoRegistroView.as_view(), name='elemento'),
]
```

## 8. Agregar las URLs al Proyecto

En `config/urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... otras URLs ...
    path('mi-app/', include('mi_nueva_app.urls')),
]
```

## 9. Crear las Migraciones

```bash
python manage.py makemigrations mi_nueva_app
python manage.py migrate
```

## 10. Crear los Templates (Opcional)

Si necesitas templates específicos, créalos en `mi_nueva_app/templates/`:

- `pages/main_mi_app.html` - Para listar registros
- `pages/steps_mi_app.html` - Para mostrar pasos

## Ventajas del Sistema Genérico

1. **Código mínimo**: Solo necesitas definir modelos, formularios y configuración
2. **Funcionalidad completa**: Obtienes automáticamente:
   - Listado con tablas
   - Activación de registros
   - Gestión de pasos
   - Formularios con validación
   - Subida de fotos
   - Mapas (si aplica)
3. **Consistencia**: Todas las aplicaciones funcionan igual
4. **Mantenibilidad**: Cambios en el sistema genérico se aplican a todas las apps

## Personalización

Puedes personalizar:
- Los formularios (manteniendo la estructura básica)
- Los templates
- La configuración de pasos
- Los modelos (heredando de las clases base) 