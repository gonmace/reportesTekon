from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from registrostxtss.forms.utils import (
    get_form_field_css_class, 
    get_form_field_css_class_simple
)


class ExampleForm(forms.Form):
    """
    Formulario de ejemplo que demuestra cómo usar la función helper
    para aplicar clases CSS automáticamente basadas en si el campo es requerido.
    """
    
    # Campos requeridos (tendrán input-success)
    nombre = forms.CharField(
        max_length=100,
        required=True,
        label='Nombre',
        help_text='Nombre completo del usuario'
    )
    
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        help_text='Correo electrónico válido'
    )
    
    # Campos opcionales (tendrán input-warning)
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label='Teléfono',
        help_text='Número de teléfono (opcional)'
    )
    
    comentarios = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label='Comentarios',
        help_text='Comentarios adicionales (opcional)'
    )
    
    edad = forms.IntegerField(
        required=False,
        label='Edad',
        help_text='Edad en años (opcional)'
    )
    
    # Campos con diferentes tipos de widgets
    pais = forms.ChoiceField(
        choices=[('CL', 'Chile'), ('AR', 'Argentina'), ('PE', 'Perú')],
        required=True,
        label='País',
        help_text='Selecciona tu país'
    )
    
    acepta_terminos = forms.BooleanField(
        required=True,
        label='Acepto los términos y condiciones',
        help_text='Debes aceptar para continuar'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "pb-4"
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        self.helper.layout = Layout(
            # Campos requeridos (verde - input-success)
            Div(
                Div(Field('nombre', css_class=get_form_field_css_class(self, 'nombre')), css_class='w-full'),
                css_class='mb-3'
            ),
            Div(
                Div(Field('email', css_class=get_form_field_css_class(self, 'email')), css_class='w-full'),
                css_class='mb-3'
            ),
            
            # Campos opcionales (amarillo - input-warning)
            Div(
                Div(Field('telefono', css_class=get_form_field_css_class(self, 'telefono')), css_class='w-1/2'),
                Div(Field('edad', css_class=get_form_field_css_class(self, 'edad')), css_class='w-1/2'),
                css_class='flex gap-3 mb-3'
            ),
            Div(
                Div(Field('comentarios', css_class=get_form_field_css_class(self, 'comentarios')), css_class='w-full'),
                css_class='mb-3'
            ),
            
            # Campos con diferentes tipos de widgets
            Div(
                Div(Field('pais', css_class=get_form_field_css_class(self, 'pais')), css_class='w-full'),
                css_class='mb-3'
            ),
            Div(
                Div(Field('acepta_terminos', css_class=get_form_field_css_class(self, 'acepta_terminos')), css_class='w-full'),
                css_class='mb-3'
            ),
            
            # Botón de envío
            Div(
                Submit('submit', 'Guardar', css_class='btn btn-success w-full mt-6 sombra'),
                css_class='text-center'
            ),
        )


class GenericForm(forms.Form):
    """
    Formulario completamente genérico que usa la versión simple
    sin clases específicas por nombre de campo.
    """
    
    titulo = forms.CharField(required=True, label='Título')
    descripcion = forms.CharField(widget=forms.Textarea, required=True, label='Descripción')
    fecha = forms.DateField(required=False, label='Fecha')
    categoria = forms.ChoiceField(
        choices=[('A', 'Categoría A'), ('B', 'Categoría B')],
        required=False,
        label='Categoría'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "pb-4"
        
        # Usar la versión simple (completamente genérica)
        self.helper.layout = Layout(
            Field('titulo', css_class=get_form_field_css_class_simple(self, 'titulo')),
            Field('descripcion', css_class=get_form_field_css_class_simple(self, 'descripcion')),
            Field('fecha', css_class=get_form_field_css_class_simple(self, 'fecha')),
            Field('categoria', css_class=get_form_field_css_class_simple(self, 'categoria')),
            Submit('submit', 'Guardar', css_class='btn btn-success')
        )


class ModelExampleForm(forms.ModelForm):
    """
    Ejemplo de formulario basado en modelo que usa la función helper.
    """
    
    class Meta:
        # Aquí especificarías tu modelo
        # model = TuModelo
        fields = ['campo1', 'campo2', 'campo3']
        labels = {
            'campo1': 'Campo 1',
            'campo2': 'Campo 2', 
            'campo3': 'Campo 3',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "pb-4"
        
        # Usar la función helper para cada campo
        self.helper.layout = Layout(
            Field('campo1', css_class=get_form_field_css_class(self, 'campo1')),
            Field('campo2', css_class=get_form_field_css_class(self, 'campo2')),
            Field('campo3', css_class=get_form_field_css_class(self, 'campo3')),
            Submit('submit', 'Guardar', css_class='btn btn-success')
        )


# Ejemplo de uso en una vista
"""
from django.views.generic.edit import CreateView
from .forms.example_form import ExampleForm, GenericForm

class ExampleCreateView(CreateView):
    form_class = ExampleForm
    template_name = 'example_form.html'
    success_url = '/success/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Formulario de Ejemplo'
        return context

class GenericCreateView(CreateView):
    form_class = GenericForm
    template_name = 'generic_form.html'
    success_url = '/success/'
""" 