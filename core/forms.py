from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Button, Div, Field
from .models.sites import Site

class SiteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        self.helper.layout = Layout(
    # Fila 1
    Div(
        Div(Field('pti_cell_id', css_class='input input-info w-full'), css_class='w-1/2  md:w-1/3 px-2'),
        Div(Field('operator_id', css_class='input input-info w-full'), css_class='w-1/2 md:w-1/3 px-2'),
        css_class='flex flex-wrap -mx-2 mb-4',
    ),

    # Fila 2
    Div(
        Div(Field('name', css_class='input input-primary w-full'), css_class='w-full sm:w-full md:w-1/3 px-2'),
        Div(Field('region', css_class='input input-info w-full'), css_class='w-full sm:w-1/2 md:w-1/3 px-2'),
        Div(Field('comuna', css_class='input input-info w-full'), css_class='w-full sm:w-1/2 md:w-1/3 px-2'),
        css_class='flex flex-wrap -mx-2 mb-4',
    ),

    # Fila 3
    Div(
        Div(Field('lat_base', css_class='input input-info w-full'), css_class='w-1/2 md:w-1/3 px-2'),
        Div(Field('lon_base', css_class='input input-info w-full'), css_class='w-1/2 md:w-1/3 px-2'),
        Div(Field('alt', css_class='input input-info w-full'), css_class='w-1/2 md:w-1/3 px-2'),
        css_class='flex flex-wrap -mx-2 mb-4',
    ),

    # Botón guardar
    Div(
        Button('cancel', 'Cancelar', css_class='btn btn-error mt-6', type='button', onclick='closeModal()'),
        Submit('submit', 'Guardar Registro', css_class='btn btn-success flex-grow mt-6'),
        css_class='flex gap-2 justify-center',
    ),
    
            
            
        )

    class Meta:
        model = Site
        fields = ['pti_cell_id', 'operator_id', 'name', 'lat_base', 'lon_base', 'alt', 'region', 'comuna']
        labels = {
            'lat_base': 'Latitud Mandato',
            'lon_base': 'Longitud Mandato',
            'alt': 'Altura (m)',
            'region': 'Región',
            'comuna': 'Comuna',
            'pti_cell_id': 'PTI ID',
            'operator_id': 'Operador ID',
            'name': 'Nombre Sitio',
        }
        widgets = {
            'pti_cell_id': forms.TextInput(attrs={'class': 'input input-success w-full text-base-content'}),
            'operator_id': forms.TextInput(attrs={'class': 'input input-success w-full text-base-content'}),
            'name': forms.TextInput(attrs={'class': 'input input-warning w-full text-base-content'}),
            'lat_base': forms.NumberInput(attrs={'class': 'input input-success w-full text-base-content', 'step': 'any'}),
            'lon_base': forms.NumberInput(attrs={'class': 'input input-success w-full text-base-content', 'step': 'any'}),
            'alt': forms.TextInput(attrs={'class': 'input input-success w-full text-base-content'}),
            'region': forms.TextInput(attrs={'class': 'input input-success w-full text-base-content'}),
            'comuna': forms.TextInput(attrs={'class': 'input input-success w-full text-base-content'}),
        }
