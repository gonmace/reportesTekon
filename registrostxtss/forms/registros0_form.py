from django import forms
from registrostxtss.models.registros_model import Registros0
from registrostxtss.models.status_registros_model import RegistrosTxTss
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, Button, Row
from crispy_forms.layout import HTML
from django.conf import settings

if settings.DEBUG:
    from rich.console import Console
    console = Console()


class Registros0Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Extraer registroId de los argumentos si está presente
        self.registro_id = kwargs.pop('registro_id', None)
        console.print(f"ahi esta el registro_id: {self.registro_id}", style="bold red")

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = "pb-4"
        self.helper.label_class
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        self.fields['lat'].help_text = 'Usa decimales negativos para el hemisferio sur.'
        self.fields['lon'].help_text = 'Usa decimales negativos para el hemisferio oeste.'
              
        # Si se proporciona registro_id, pre-seleccionar el registro correspondiente
        if self.registro_id and not self.instance.pk:
            registro_obj = RegistrosTxTss.objects.get(id=self.registro_id)
            sitio = registro_obj.sitio
            self.initial['registro'] = registro_obj
            self.fields['registro'].widget = forms.HiddenInput()
            # Solo establecer altura si existe el campo alt en el sitio
            if hasattr(sitio, 'alt') and sitio.alt:
                self.initial['altura'] = sitio.alt 

      
                # HTML dinámico
        header_html = f"""
        <div class="bg-base-200 p-4 rounded-t-lg pb-1">
            <h2>{sitio.pti_cell_id or ''}</h2>
            <h3 class="text-sm font-semibold mb-3">{sitio.operator_id or ''} - {sitio.name or '__'}</h3>
        </div>
        """
        
        btn_ubicar_mapa_html = f"""
            <button type="button"
            id="btn-ubicar-mapa"
            class="btn p-0 h-10 sm:h-12 w-10 sm:w-12 mt-auto mb-2 mr-2">
            <svg width="64px" height="64px" viewBox="0 0 1024 1024" class="icon" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M640 213.333333L384 128 128 213.333333v682.666667l256-85.333333 256 85.333333 256-85.333333V128z" fill="#FFECB3"></path><path d="M384 128v682.666667l256 85.333333V213.333333z" fill="#FFE082"></path><path d="M640 320c-82.496 0-149.333333 70.250667-149.333333 156.821333S640 768 640 768s149.333333-204.629333 149.333333-291.178667S722.496 320 640 320z" fill="#F44336"></path><path d="M640 469.333333m-64 0a64 64 0 1 0 128 0 64 64 0 1 0-128 0Z" fill="#FFEBEE"></path></g></svg>
        </button>
        
        """
            
        self.helper.layout = Layout(
            HTML(header_html),
            Field('registro'),
            
            Div(
                HTML(btn_ubicar_mapa_html),
                Div(
                    Field('lat', 
                          css_class='input input-bordered w-full rounded-r-none',
                          placeholder='Latitud',
                          help_text='Latitud de la ubicación de la inspección',
                          ),
                    Button('lat_grados',
                           "°", 
                           css_class='bg-warning mt-auto mb-2 text-3xl rounded-l-none',
                           data_target='lat',
                           ),
                    css_class='flex flex-row flex-1 min-w-0'
                ),
                Div(
                    Field('lon', css_class='input input-bordered w-full rounded-r-none'),
                    Button('lon_grados',
                           "°", 
                           css_class='bg-warning mt-auto mb-2 text-3xl rounded-l-none',
                           data_target='lon',
                           ),
                    css_class='flex flex-row flex-1 min-w-0'
                ),
                css_class='flex flex-row items-start gap-1'
            ),
            # Altura
            Div(
                Field('altura', css_class='input input-bordered w-full'),
                css_class='mb-4'
            ),
            # Dimensiones y deslindes
            Div(
                Div(Field('dimensiones', css_class='input input-bordered w-full'), css_class='w-1/2 px-2'),
                Div(Field('deslindes', css_class='input input-bordered w-full'), css_class='w-1/2 px-2'),
                css_class='flex flex-wrap -mx-2 mb-4',
            ),
            # Botón de envío
            Div(
                Submit('submit', 'Guardar Registro', css_class='btn btn-success w-full mt-6'),
                css_class='text-center'
            ),
        )

    
    class Meta:
        model = Registros0
        fields = ['registro', 'lat', 'lon', 'altura', 'dimensiones', 'deslindes']
        labels = {
            'registro': 'Registro Tx/Tss',
            'lat': 'Latitud',
            'lon': 'Longitud',
            'altura': 'Altura (m)',
            'dimensiones': 'Dimensiones',
            'deslindes': 'Deslindes',
        }
