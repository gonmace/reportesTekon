"""
Ejemplo de cómo usar la vista genérica para diferentes modelos.

Este archivo muestra cómo crear vistas específicas para diferentes modelos
usando la vista genérica GenericRegistroView con formularios específicos.
"""

from registrostxtss.views.generic_views import GenericRegistroView
from registrostxtss.r_sitio.models import RSitio
from registrostxtss.r_acceso.models import RAcceso


class RSitioView(GenericRegistroView):
    """
    Vista específica para el modelo RSitio usando la vista genérica.
    """
    from registrostxtss.r_sitio.form import RSitioForm
    form_class = RSitioForm
    
    def setup(self, request, *args, **kwargs):
        """Configura la vista con el modelo RSitio."""
        kwargs['model_class'] = RSitio
        kwargs['etapa'] = 'sitio'
        super().setup(request, *args, **kwargs)


class RAccesoView(GenericRegistroView):
    """
    Vista específica para el modelo RAcceso usando la vista genérica.
    """
    from registrostxtss.r_acceso.form import RAccesoForm
    form_class = RAccesoForm
    
    def setup(self, request, *args, **kwargs):
        """Configura la vista con el modelo RAcceso."""
        kwargs['model_class'] = RAcceso
        kwargs['etapa'] = 'acceso'
        super().setup(request, *args, **kwargs)


# Ejemplo de cómo crear una vista para un modelo futuro
# class REquipamientoView(GenericRegistroView):
#     """
#     Vista específica para el modelo REquipamiento usando la vista genérica.
#     """
#     from registrostxtss.r_equipamiento.form import REquipamientoForm
#     form_class = REquipamientoForm
#     
#     def setup(self, request, *args, **kwargs):
#         """Configura la vista con el modelo REquipamiento."""
#         kwargs['model_class'] = REquipamiento
#         kwargs['etapa'] = 'equipamiento'
#         super().setup(request, *args, **kwargs)


# Ejemplo de cómo crear una vista para un modelo de seguridad
# class RSeguridadView(GenericRegistroView):
#     """
#     Vista específica para el modelo RSeguridad usando la vista genérica.
#     """
#     from registrostxtss.r_seguridad.form import RSeguridadForm
#     form_class = RSeguridadForm
#     
#     def setup(self, request, *args, **kwargs):
#         """Configura la vista con el modelo RSeguridad."""
#         kwargs['model_class'] = RSeguridad
#         kwargs['etapa'] = 'seguridad'
#         super().setup(request, *args, **kwargs)


"""
USO EN URLs:

Para usar estas vistas en tus URLs, simplemente agrega las rutas correspondientes:

# registrostxtss/urls.py
from django.urls import path
from .r_sitio.views import RSitioView
from .r_acceso.views import RAccesoView

urlpatterns = [
    path('sitio/<int:registro_id>/', RSitioView.as_view(), name='r_sitio'),
    path('acceso/<int:registro_id>/', RAccesoView.as_view(), name='r_acceso'),
    # Agregar más rutas según sea necesario
]

VENTAJAS DE LA VISTA GENÉRICA:

1. **Reutilización de código**: No necesitas escribir la misma lógica para cada modelo
2. **Consistencia**: Todas las vistas tienen el mismo comportamiento base
3. **Mantenimiento**: Los cambios en la lógica común se aplican automáticamente
4. **Flexibilidad**: Cada modelo puede tener su propio formulario personalizado
5. **Escalabilidad**: Agregar nuevos modelos es muy fácil

CARACTERÍSTICAS AUTOMÁTICAS DE LA VISTA GENÉRICA:

- ✅ Validación de formularios
- ✅ Pre-llenado de datos del sitio
- ✅ Manejo de edición vs creación
- ✅ Redirección automática
- ✅ Manejo de errores
- ✅ Breadcrumbs automáticos
- ✅ Interfaz consistente
- ✅ Contexto automático

FORMULARIOS ESPECÍFICOS:

Cada modelo debe tener su propio formulario con:
- Layout personalizado con crispy forms
- Campos específicos del modelo
- Validaciones específicas
- Help text personalizado
- Estilos específicos

EJEMPLO DE FORMULARIO ESPECÍFICO:

# registrostxtss/r_mi_modelo/form.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
from registrostxtss.r_mi_modelo.models import RMiModelo

class RMiModeloForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.registro_id = kwargs.pop('registro_id', None)
        super().__init__(*args, **kwargs)
        
        # Configurar crispy forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "pb-4"
        
        # Layout específico para este modelo
        self.helper.layout = Layout(
            HTML('<div class="header">Mi Modelo</div>'),
            Field('registro'),
            Field('campo_especifico_1'),
            Field('campo_especifico_2'),
            Submit('submit', 'Guardar', css_class='btn btn-success')
        )
    
    class Meta:
        model = RMiModelo
        fields = ['registro', 'campo_especifico_1', 'campo_especifico_2']
        labels = {
            'campo_especifico_1': 'Mi Campo 1',
            'campo_especifico_2': 'Mi Campo 2',
        }

PERSONALIZACIÓN:

Si necesitas personalizar una vista específica, puedes sobrescribir métodos:

class RAccesoView(GenericRegistroView):
    form_class = RAccesoForm
    
    def setup(self, request, *args, **kwargs):
        kwargs['model_class'] = RAcceso
        kwargs['etapa'] = 'acceso'
        super().setup(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar contexto específico para acceso
        context['custom_data'] = 'valor específico'
        return context
    
    def form_valid(self, form):
        # Lógica específica antes de guardar
        instance = form.save(commit=False)
        instance.custom_field = 'valor'
        instance.save()
        return super().form_valid(form)
""" 