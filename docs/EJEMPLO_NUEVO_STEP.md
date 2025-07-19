# Ejemplo: Agregando un Nuevo Step "Instalación"

Este ejemplo muestra cómo agregar un nuevo step llamado "Instalación" que tendrá formulario, fotos y mapa.

## Paso 1: Crear el Modelo

```python
# registrostxtss/r_instalacion/models.py
from django.db import models
from core.models import BaseModel
from registrostxtss.models.registrostxtss import RegistrosTxTss
from registrostxtss.models.validators import validar_latitud, validar_longitud
from registrostxtss.models.completeness_checker import check_model_completeness


class RInstalacion(BaseModel):
    registro = models.ForeignKey(RegistrosTxTss, on_delete=models.CASCADE, verbose_name='Registro')
    lat = models.FloatField(validators=[validar_latitud], verbose_name='Latitud Instalación')
    lon = models.FloatField(validators=[validar_longitud], verbose_name='Longitud Instalación')
    tipo_instalacion = models.CharField(max_length=100, verbose_name='Tipo de Instalación')
    estado = models.CharField(max_length=50, verbose_name='Estado')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro Instalación'
        verbose_name_plural = 'Registros Instalación'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.registro} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    @staticmethod
    def get_etapa():
        return 'instalacion'
    
    @staticmethod
    def get_actives():
        return RInstalacion.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness(rinstalacion_id):
        return check_model_completeness(RInstalacion, rinstalacion_id)
```

## Paso 2: Crear el Formulario

```python
# registrostxtss/r_instalacion/form.py
from django import forms
from registrostxtss.r_instalacion.models import RInstalacion
from registrostxtss.models.registrostxtss import RegistrosTxTss
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from registrostxtss.forms.utils import get_form_field_css_class

class RInstalacionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.registro_id = kwargs.pop('registro_id', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = "pb-4"
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        # Configurar campos
        self.fields['lat'].help_text = 'Grados decimales.'
        self.fields['lon'].help_text = 'Grados decimales.'
        
        # Pre-seleccionar registro si se proporciona
        if self.registro_id and not self.instance.pk:
            try:
                registro_obj = RegistrosTxTss.objects.get(id=self.registro_id)
                self.initial['registro'] = registro_obj
                self.fields['registro'].widget = forms.HiddenInput()
            except RegistrosTxTss.DoesNotExist:
                pass
        elif self.instance.pk:
            self.fields['registro'].widget = forms.HiddenInput()
        
        # Layout del formulario
        self.helper.layout = Layout(
            Field('registro'),
            Div(
                Div(Field('lat', 
                          template='forms/lat_lon_input.html',
                          label='Latitud',
                          placeholder='ej: -33.432611',
                          css_class=get_form_field_css_class(self, 'lat')
                          ), css_class='w-1/2'),
                Div(Field('lon', 
                          template='forms/lat_lon_input.html', 
                          label='Longitud', 
                          placeholder='ej: -70.669261',
                          css_class=get_form_field_css_class(self, 'lon')
                          ), css_class='w-1/2'),
                css_class='flex gap-3 mb-3'
            ),
            Div(
                Div(Field('tipo_instalacion', css_class=get_form_field_css_class(self, 'tipo_instalacion')), css_class='w-1/2'),
                Div(Field('estado', css_class=get_form_field_css_class(self, 'estado')), css_class='w-1/2'),
                css_class='flex gap-3 mb-3'
            ),
            Div(Field('comentarios', css_class=get_form_field_css_class(self, 'comentarios')), css_class='w-full'),
            Div(
                Submit('submit', 'Guardar Instalación', css_class='btn btn-success w-full mt-4 sombra'),
                css_class='text-center'
            )
        )
    
    class Meta:
        model = RInstalacion
        fields = ['registro', 'lat', 'lon', 'tipo_instalacion', 'estado', 'comentarios']
        labels = {
            'registro': 'Registro Tx/Tss',
            'lat': 'Latitud',
            'lon': 'Longitud',
            'tipo_instalacion': 'Tipo de Instalación',
            'estado': 'Estado',
            'comentarios': 'Comentarios',
        }
```

## Paso 3: Crear la Vista

```python
# registrostxtss/r_instalacion/views.py
from registrostxtss.views.generic_views import GenericRegistroView
from registrostxtss.r_instalacion.models import RInstalacion
from registrostxtss.r_instalacion.form import RInstalacionForm

class RInstalacionView(GenericRegistroView):
    """
    Vista específica para el modelo RInstalacion usando la vista genérica.
    """
    form_class = RInstalacionForm
    
    def setup(self, request, *args, **kwargs):
        """Configura la vista con el modelo RInstalacion."""
        kwargs['model_class'] = RInstalacion
        kwargs['etapa'] = 'instalacion'
        super().setup(request, *args, **kwargs)
```

## Paso 4: Agregar URL

```python
# registrostxtss/urls.py
from .r_instalacion.views import RInstalacionView

urlpatterns = [
    # ... URLs existentes
    path("registrostxtss/<int:registro_id>/instalacion/", RInstalacionView.as_view(), name="r_instalacion"),
]
```

## Paso 5: Configurar en StepsRegistroView

```python
# registrostxtss/views/base_steps_view.py
def get_steps_config(self) -> Dict[str, Dict[str, Any]]:
    from registrostxtss.r_sitio.models import RSitio
    from registrostxtss.r_acceso.models import RAcceso
    from registrostxtss.r_empalme.models import REmpalme
    from registrostxtss.r_instalacion.models import RInstalacion  # Nuevo import
    
    return {
        'sitio': {
            'model_class': RSitio,
            'elements': {
                'photos': {
                    'enabled': True,
                    'min_count': 4,
                    'required': False,
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
                            'size': 'large',   
                        },
                        'coordinates_2': {
                            'model': 'current',
                            'lat': 'lat',
                            'lon': 'lon',
                            'label': 'Inspección',
                            'color': '#F59E0B',
                            'size': 'mid',
                        },
                    }
                },
                'desfase': {
                    'enabled': True,
                    'reference': 'site',
                    'description': 'Distancia desde el mandato',
                }
            },
            'order': 1,
            'title': 'Sitio',
            'description': 'Información general del sitio.',
        },
        'acceso': {
            'model_class': RAcceso,
            'elements': {
                'photos': {
                    'enabled': True,
                    'min_count': 4,
                    'required': False,
                },
                'map': {
                    'enabled': True,
                    'coordinates': {
                        'coordinates_1': {
                            'model': 'current',
                            'lat': 'lat',
                            'lon': 'lon',
                            'label': 'Acceso',
                            'color': '#8B5CF6',
                            'size': 'large',
                        },
                    }
                },
                'desfase': {
                    'enabled': True,
                    'reference': 'site',
                    'description': 'Distancia desde el mandato',
                }
            },
            'order': 2,
            'title': 'Acceso',
            'description': 'Información sobre el acceso al sitio.',
        },
        'empalme': {
            'model_class': REmpalme,
            'elements': {
                'photos': {
                    'enabled': True,
                    'min_count': 3,
                    'required': False,
                },
                'map': {
                    'enabled': True,
                    'coordinates': {
                        'coordinates_1': {
                            'model': 'rsitio', 
                            'lat': 'lat',
                            'lon': 'lon',
                            'label': 'Sitio',
                            'color': '#F59E0B',
                            'size': 'large',   
                        },
                        'coordinates_2': {
                            'model': 'current',
                            'lat': 'lat',
                            'lon': 'lon',
                            'label': 'Empalme',
                            'color': '#e60000',
                            'size': 'mid',     
                        },
                        'coordinates_3': {
                            'model': 'site',
                            'lat': 'lat_base',
                            'lon': 'lon_base',
                            'label': 'Mandato',
                            'color': '#3B82F6',
                            'size': 'large',     
                        },
                    }
                },
                'desfase': {
                    'enabled': True,
                    'reference': 'site',
                    'description': 'Distancia desde el mandato',
                }
            },
            'order': 3,
            'title': 'Empalme',
            'description': 'Información sobre el empalme.',
        },
        # NUEVO STEP: Instalación
        'instalacion': {
            'model_class': RInstalacion,
            'elements': {
                'photos': {
                    'enabled': True,
                    'min_count': 2,
                    'required': True,  # Las fotos son obligatorias
                },
                'map': {
                    'enabled': True,
                    'coordinates': {
                        'coordinates_1': {
                            'model': 'current',
                            'lat': 'lat',
                            'lon': 'lon',
                            'label': 'Instalación',
                            'color': '#10B981',
                            'size': 'large',
                        },
                        'coordinates_2': {
                            'model': 'rsitio',
                            'lat': 'lat',
                            'lon': 'lon',
                            'label': 'Sitio',
                            'color': '#F59E0B',
                            'size': 'mid',
                        },
                    }
                },
                'desfase': {
                    'enabled': True,
                    'reference': 'site',
                    'description': 'Distancia desde el mandato',
                }
            },
            'order': 4,
            'title': 'Instalación',
            'description': 'Información sobre la instalación del equipo.',
        },
    }
```

## Paso 6: Crear Migración

```bash
python manage.py makemigrations registrostxtss
python manage.py migrate
```

## Resultado

Después de estos pasos, tendrás un nuevo step "Instalación" que:

- ✅ **Formulario**: Con campos para lat/lon, tipo de instalación, estado y comentarios
- ✅ **Fotos**: 2 fotos mínimas y obligatorias (se mostrará un asterisco si faltan)
- ✅ **Mapa**: Con 2 coordenadas (Instalación + Sitio)
- ✅ **Desfase**: Calcula la distancia desde el sitio base
- ✅ **Orden**: Aparece como el 4to step en la lista

## Configuraciones Alternativas

### Solo Formulario
```python
'instalacion': {
    'model_class': RInstalacion,
    'elements': {
        # No se especifican elementos adicionales
    },
    'order': 4,
    'title': 'Instalación',
    'description': 'Información básica de la instalación.',
}
```

### Formulario + Fotos (sin mapa)
```python
'instalacion': {
    'model_class': RInstalacion,
    'elements': {
        'photos': {
            'enabled': True,
            'min_count': 3,
            'required': False,
        }
    },
    'order': 4,
    'title': 'Instalación',
    'description': 'Información y fotos de la instalación.',
}
```

### Formulario + Mapa (sin fotos)
```python
'instalacion': {
    'model_class': RInstalacion,
    'elements': {
        'map': {
            'enabled': True,
            'coordinates': {
                'coordinates_1': {
                    'model': 'current',
                    'lat': 'lat',
                    'lon': 'lon',
                    'label': 'Instalación',
                    'color': '#10B981',
                    'size': 'large',
                }
            }
        }
    },
    'order': 4,
    'title': 'Instalación',
    'description': 'Ubicación de la instalación.',
}
```

## Ventajas del Ejemplo

1. **Flexibilidad**: Puedes configurar exactamente lo que necesitas
2. **Reutilización**: Usa las vistas genéricas existentes
3. **Consistencia**: Sigue el mismo patrón que los otros steps
4. **Mantenibilidad**: Todo está centralizado en la configuración
5. **Escalabilidad**: Fácil agregar más elementos en el futuro 