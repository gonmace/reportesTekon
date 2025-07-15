from django import forms
from registrostxtss.r_empalme.models import REmpalme
from registrostxtss.models.main_registrostxtss import RegistrosTxTss
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from crispy_forms.layout import HTML
from django.conf import settings
from registrostxtss.forms.utils import get_form_field_css_class

if settings.DEBUG:
    from rich.console import Console
    console = Console()


class REmpalmeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Extraer registroId de los argumentos si está presente
        self.registro_id = kwargs.pop('registro_id', None)

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = "pb-4"
        self.helper.label_class
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        self.fields['lat'].help_text = 'Grados decimales.'
        self.fields['lon'].help_text = 'Grados decimales.'
        self.fields['no_poste'].help_text = 'Número de poste.'
        
        # Si se proporciona registro_id, pre-seleccionar el registro correspondiente
        if self.registro_id and not self.instance.pk:
            try:
                registro_obj = RegistrosTxTss.objects.get(id=self.registro_id)
                sitio = registro_obj.sitio
                self.initial['registro'] = registro_obj
                self.fields['registro'].widget = forms.HiddenInput()
            except RegistrosTxTss.DoesNotExist:
                pass
        elif self.instance.pk:
            # Si estamos editando una instancia existente, ocultar el campo registro
            self.fields['registro'].widget = forms.HiddenInput()
            sitio = self.instance.registro.sitio
        else:
            sitio = None
        
        btn_ubicar_mapa_html = f"""
        <button type="button"
            id="btn-ubicar-mapa"
            class="btn p-0 h-10 sm:h-12 w-10 sm:w-12 my-auto">
                <svg width="64px" height="64px" viewBox="0 0 1024 1024" class="icon sombra" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M640 213.333333L384 128 128 213.333333v682.666667l256-85.333333 256 85.333333 256-85.333333V128z" fill="#FFECB3"></path><path d="M384 128v682.666667l256 85.333333V213.333333z" fill="#FFE082"></path><path d="M640 320c-82.496 0-149.333333 70.250667-149.333333 156.821333S640 768 640 768s149.333333-204.629333 149.333333-291.178667S722.496 320 640 320z" fill="#F44336"></path><path d="M640 469.333333m-64 0a64 64 0 1 0 128 0 64 64 0 1 0-128 0Z" fill="#FFEBEE"></path></g></svg>
        </button>
        
        """
            
        self.helper.layout = Layout(
            Field('registro'),
            Div(
                HTML(btn_ubicar_mapa_html),
                Div(Field('lat',
                          template='forms/lat_lon_input.html',
                          label='Latitud',
                          placeholder='ej: -33.432611',
                          css_class=get_form_field_css_class(self, 'lat')
                          )
                    ),
                Div(Field('lon', 
                          template='forms/lat_lon_input.html', 
                          label='Longitud', 
                          placeholder='ej: -70.669261',
                          css_class=get_form_field_css_class(self, 'lon')
                          )
                    ),
                css_class='flex flex-row justify-between gap-3 mb-3'
            ),
            Div(
                Div(Field('proveedor', css_class=get_form_field_css_class(self, 'proveedor')), css_class='w-1/2'),
                Div(Field('capacidad', css_class=get_form_field_css_class(self, 'capacidad')), css_class='w-1/2'),
                css_class='flex flex-row justify-between gap-3'
            ),
            Div(
                Field('no_poste', css_class=f"{get_form_field_css_class(self, 'no_poste')} w-full" ),
                css_class='max-w-1/2'
            ),
            Div(Field('comentarios', css_class=get_form_field_css_class(self, 'comentarios')), css_class='w-full'),
            Div(
                Submit('submit', 'Guardar Registro', css_class='btn btn-success w-full mt-4 sombra'),
                css_class='text-center'
            ),
        )

    
    class Meta:
        model = REmpalme
        fields = ['registro', 'lat', 'lon', 'proveedor', 'capacidad', 'no_poste', 'comentarios']
        labels = {
            'registro': 'Registro Tx/Tss',
            'lat': 'Latitud',
            'lon': 'Longitud',
            'proveedor': 'Proveedor',
            'capacidad': 'Capacidad',
            'no_poste': 'No. Poste',
            'comentarios': 'Comentarios',
        }
