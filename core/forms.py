from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Button
from .models.sites import Site


class SiteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.label_class = 'text-sm font-normal text-secondary-content'
        self.helper.field_class = 'mb-4'
        
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
