from django import forms
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
from registros.r_empalme.models import REmpalme
from registros.models.registrostxtss import Registro
from registros.forms.utils import get_form_field_css_class
from rich.console import Console

console = Console()

class REmpalmeForm(forms.ModelForm):
    registro_id = forms.CharField(widget=forms.HiddenInput())
    
    class Meta:
        model = REmpalme
        fields = ['proveedor', 'capacidad', 'no_poste', 'comentarios']
        labels = {
            'proveedor': 'Proveedor',
            'capacidad': 'Capacidad',
            'no_poste': 'No. Poste',
            'comentarios': 'Comentarios'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get the registro object
        registro_id = kwargs.get('initial', {}).get('registro_id')
        if registro_id:
            try:
                registro_obj = Registro.objects.get(pk=registro_id)
                self.fields['registro_id'].initial = registro_id
            except Registro.DoesNotExist:
                pass
        
        # Form helper configuration
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        
        # Custom HTML for map location button
        btn_ubicar_mapa_html = '''
        <button type="button"
            id="btn-ubicar-mapa"
            class="btn p-0 h-10 sm:h-12 w-10 sm:w-12 my-auto">
                <svg width="64px" height="64px" viewBox="0 0 1024 1024" class="icon sombra" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M640 213.333333L384 128 128 213.333333v682.666667l256-85.333333 256 85.333333 256-85.333333V128z" fill="#FFECB3"></path><path d="M384 128v682.666667l256 85.333333V213.333333z" fill="#FFE082"></path><path d="M640 320c-82.496 0-149.333333 70.250667-149.333333 156.821333S640 768 640 768s149.333333-204.629333 149.333333-291.178667S722.496 320 640 320z" fill="#F44336"></path><path d="M640 469.333333m-64 0a64 64 0 1 0 128 0 64 64 0 1 0-128 0Z" fill="#FFEBEE"></path></g></svg>
        </button>
        '''
        
        # Form layout
        self.helper.layout = Layout(
            Field('registro_id'),
            Div(
                Div(
                    Field('proveedor', css_class='w-1/2'),
                    css_class='flex flex-row justify-between gap-3 mb-3'
                ),
                Div(
                    Field('capacidad', css_class='w-full'),
                    css_class='flex flex-row justify-between gap-3'
                ),
                Div(
                    Field('no_poste', css_class='max-w-1/2'),
                    css_class='flex flex-row justify-between gap-3'
                ),
                Div(
                    Field('comentarios', css_class='w-full'),
                    css_class='flex flex-row justify-between gap-3'
                ),
                css_class='pb-4'
            ),
            Submit('submit', 'Guardar Registro', css_class='btn btn-success w-full mt-4 sombra text-center')
        )
        
        # Apply CSS classes to form fields
        for field_name, field in self.fields.items():
            if field_name != 'registro_id':
                field.widget.attrs.update({
                    'class': get_form_field_css_class(field_name)
                }) 