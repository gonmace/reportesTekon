"""
Formularios para registros TX/TSS.
"""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from .models import RSitio, RAcceso, REmpalme


class RSitioForm(forms.ModelForm):
    """Formulario para el paso Sitio."""
    
    def __init__(self, *args, **kwargs):
        self.registro_id = kwargs.pop('registro_id', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "pb-4"
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        self.helper.layout = Layout(
            Field('lat', css_class='input input-success sombra'),
            Field('lon', css_class='input input-success sombra'),
            Field('altura', css_class='input input-success sombra'),
            Field('dimensiones', css_class='input input-success sombra'),
            Field('deslindes', css_class='input input-success sombra'),
            Field('comentarios', css_class='textarea textarea-warning sombra rows-2'),
            Submit('submit', 'Guardar', css_class='btn btn-primary'),
        )
    
    class Meta:
        model = RSitio
        fields = ['lat', 'lon', 'altura', 'dimensiones', 'deslindes', 'comentarios']
        widgets = {
            'lat': forms.NumberInput(attrs={'class': 'input input-success sombra', 'step': 'any'}),
            'lon': forms.NumberInput(attrs={'class': 'input input-success sombra', 'step': 'any'}),
            'altura': forms.TextInput(attrs={'class': 'input input-success sombra'}),
            'dimensiones': forms.TextInput(attrs={'class': 'input input-success sombra'}),
            'deslindes': forms.TextInput(attrs={'class': 'input input-success sombra'}),
            'comentarios': forms.Textarea(attrs={'class': 'textarea textarea-warning sombra rows-2'}),
        }


class RAccesoForm(forms.ModelForm):
    """Formulario para el paso Acceso."""
    
    def __init__(self, *args, **kwargs):
        self.registro_id = kwargs.pop('registro_id', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "pb-4"
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        self.helper.layout = Layout(
            Field('tipo_suelo', css_class='input input-success sombra'),
            Field('distancia', css_class='input input-success sombra'),
            Field('comentarios', css_class='textarea textarea-warning sombra rows-2'),
            Submit('submit', 'Guardar', css_class='btn btn-primary'),
        )
    
    class Meta:
        model = RAcceso
        fields = ['tipo_suelo', 'distancia', 'comentarios']
        widgets = {
            'tipo_suelo': forms.TextInput(attrs={'class': 'input input-success sombra'}),
            'distancia': forms.TextInput(attrs={'class': 'input input-success sombra'}),
            'comentarios': forms.Textarea(attrs={'class': 'textarea textarea-warning sombra rows-2'}),
        }


class REmpalmeForm(forms.ModelForm):
    """Formulario para el paso Empalme."""
    
    def __init__(self, *args, **kwargs):
        self.registro_id = kwargs.pop('registro_id', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "pb-4"
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        self.helper.layout = Layout(
            Field('proveedor', css_class='input input-success sombra'),
            Field('capacidad', css_class='input input-success sombra'),
            Field('comentarios', css_class='textarea textarea-warning sombra rows-2'),
            Submit('submit', 'Guardar', css_class='btn btn-primary'),
        )
    
    class Meta:
        model = REmpalme
        fields = ['proveedor', 'capacidad', 'comentarios']
        widgets = {
            'proveedor': forms.TextInput(attrs={'class': 'input input-success sombra'}),
            'capacidad': forms.TextInput(attrs={'class': 'input input-success sombra'}),
            'comentarios': forms.Textarea(attrs={'class': 'textarea textarea-warning sombra rows-2'}),
        } 