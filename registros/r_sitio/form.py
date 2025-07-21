from django import forms
from registros.r_sitio.models import RSitio
from registros.models.registrostxtss import Registros
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
from django.conf import settings
from registros.forms.utils import get_form_field_css_class
from rich.console import Console

console = Console()

class RSitioForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.registro_id = kwargs.pop('registro_id', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'pb-4'
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        # Set help text for fields
        self.fields['lat'].help_text = 'Grados decimales.'
        self.fields['lon'].help_text = 'Grados decimales.'
        self.fields['dimensiones'].help_text = 'Dimensiones del sitio'
        self.fields['altura'].help_text = 'Metros'
        self.fields['deslindes'].help_text = 'Distancia a los bordes de la propiedad, las distancias cortas deben ser precisas.'
        
        try:
            if self.registro_id and not self.instance.pk:
                registro_obj = Registros.objects.get(id=self.registro_id)
                sitio = registro_obj.sitio
                self.initial['registro'] = registro_obj
                self.fields['registro'].widget = forms.HiddenInput()
            elif self.instance.pk:
                self.fields['registro'].widget = forms.HiddenInput()
                sitio = self.instance.registro.sitio
            else:
                sitio = None
        except Registros.DoesNotExist:
            sitio = None
        
        # HTML for map location button
        btn_ubicar_mapa_html = '''
        <button type="button"
            id="btn-ubicar-mapa"
            class="btn p-0 h-10 sm:h-12 w-10 sm:w-12 my-auto">
                <svg width="64px" height="64px" viewBox="0 0 1024 1024" class="icon sombra" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M640 213.333333L384 128 128 213.333333v682.666667l256-85.333333 256 85.333333 256-85.333333V128z" fill="#FFECB3"></path><path d="M384 128v682.666667l256 85.333333V213.333333z" fill="#FFE082"></path><path d="M640 320c-82.496 0-149.333333 70.250667-149.333333 156.821333S640 768 640 768s149.333333-204.629333 149.333333-291.178667S722.496 320 640 320z" fill="#F44336"></path><path d="M640 469.333333m-64 0a64 64 0 1 0 128 0 64 64 0 1 0-128 0Z" fill="#FFEBEE"></path></g></svg>
        </button>
        '''
        
        self.helper.layout = Layout(
            Field('registro'),
            Div(
                Div(
                    HTML('{% include "forms/lat_lon_input.html" %}'),
                    css_class='flex flex-row justify-between gap-3 mb-3'
                ),
                Div(
                    Field('lat', css_class=get_form_field_css_class(self, 'lat'), css_class='max-w-16'),
                    Field('lon', css_class=get_form_field_css_class(self, 'lon'), css_class='max-w-16'),
                    css_class='flex flex-row justify-between gap-3 mb-3'
                ),
                Div(
                    Field('dimensiones', css_class=get_form_field_css_class(self, 'dimensiones'), css_class='max-w-90'),
                    Field('altura', css_class=get_form_field_css_class(self, 'altura'), css_class='w-full sm:w-3/4'),
                    css_class='flex sm:flex-row flex-col justify-between gap-3'
                ),
                Div(
                    Field('deslindes', css_class=get_form_field_css_class(self, 'deslindes'), css_class='w-full'),
                    css_class='flex flex-row justify-between gap-3'
                ),
                Div(
                    Field('comentarios', css_class=get_form_field_css_class(self, 'comentarios'), css_class='w-full'),
                    css_class='mb-3'
                ),
                Div(
                    Submit('submit', 'Guardar Registro', css_class='btn btn-success w-full mt-4 sombra'),
                    css_class='text-center'
                ),
            )
        )
    
    class Meta:
        model = RSitio
        fields = ['registro', 'lat', 'lon', 'dimensiones', 'altura', 'deslindes', 'comentarios']
        labels = {
            'lat': 'Latitud',
            'lon': 'Longitud',
            'dimensiones': 'Dimensiones del sitio',
            'altura': 'Altura',
            'deslindes': 'Deslindes',
            'comentarios': 'Comentarios',
        } 