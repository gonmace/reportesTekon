from django import forms
from registrostxtss.r_acceso.models import RAcceso
from registrostxtss.models.main_registrostxtss import RegistrosTxTss
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from crispy_forms.layout import HTML
from django.conf import settings

if settings.DEBUG:
    from rich.console import Console
    console = Console()


class RAccesoForm(forms.ModelForm):
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
        
        self.fields['acceso_sitio'].help_text = 'Descripción del acceso al sitio'
        self.fields['acceso_sitio_construccion'].help_text = 'Descripción del acceso al sitio para construcción'
        self.fields['longitud_acceso_sitio'].help_text = 'Longitud del acceso al sitio'
        self.fields['longitud_acceso_construccion'].help_text = 'Longitud del acceso al sitio para construcción'
        self.fields['tipo_suelo'].help_text = 'Tipo de suelo de sitio y huella'
        self.fields['obstaculos'].help_text = 'Edificaciones cercanas / obstáculos'
        self.fields['adicionales'].help_text = 'Trabajos adicionales a considerar'
        
        # Si se proporciona registro_id, pre-seleccionar el registro correspondiente
        if self.registro_id and not self.instance.pk:
            try:
                registro_obj = RegistrosTxTss.objects.get(id=self.registro_id)
                sitio = registro_obj.sitio
                self.initial['registro'] = registro_obj
                self.fields['registro'].widget = forms.HiddenInput()
                # Solo establecer altura si existe el campo alt en el sitio
                if hasattr(sitio, 'alt') and sitio.alt:
                    self.initial['altura'] = sitio.alt
            except RegistrosTxTss.DoesNotExist:
                pass
        elif self.instance.pk:
            # Si estamos editando una instancia existente, ocultar el campo registro
            self.fields['registro'].widget = forms.HiddenInput()
            sitio = self.instance.registro.sitio
        else:
            sitio = None

        # HTML dinámico
        if sitio:
            header_html = f"""
            <div class="bg-base-200 rounded-t-lg pb-1">
                <h2>{sitio.pti_cell_id or ''}</h2>
                <h3 class="text-sm font-semibold mb-3">{sitio.operator_id or ''} - {sitio.name or '__'}</h3>
            </div>
            """
        else:
            header_html = """
            <div class="bg-base-200 rounded-t-lg pb-1">
                <h2>Registro no encontrado</h2>
            </div>
            """
        
        btn_ubicar_mapa_html = f"""
        <button type="button"
            id="btn-ubicar-mapa"
            class="btn p-0 h-10 sm:h-12 w-10 sm:w-12 my-auto">
                <svg width="64px" height="64px" viewBox="0 0 1024 1024" class="icon sombra" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M640 213.333333L384 128 128 213.333333v682.666667l256-85.333333 256 85.333333 256-85.333333V128z" fill="#FFECB3"></path><path d="M384 128v682.666667l256 85.333333V213.333333z" fill="#FFE082"></path><path d="M640 320c-82.496 0-149.333333 70.250667-149.333333 156.821333S640 768 640 768s149.333333-204.629333 149.333333-291.178667S722.496 320 640 320z" fill="#F44336"></path><path d="M640 469.333333m-64 0a64 64 0 1 0 128 0 64 64 0 1 0-128 0Z" fill="#FFEBEE"></path></g></svg>
        </button>
        
        """
            
        self.helper.layout = Layout(
            HTML(header_html),
            Field('registro'),
            Div(
                HTML(btn_ubicar_mapa_html),
                
                css_class='flex flex-row justify-between gap-3 mb-3'
            ),
            Div(
                Div(Field('acceso_sitio', css_class='input input-warning w-full'), css_class='max-w-16'),
                Div(
                    Div(Field('acceso_sitio_construccion',
                            css_class='input w-full input-warning',
                            placeholder='ej: 15x15 m',
                            ), css_class='max-w-90'),
                    Div(Field('longitud_acceso_sitio', 
                            css_class='input input-warning w-full',
                            placeholder='ej: 18 / 18 +50 / +100 m',
                            ), css_class=' w-full sm:w-3/4'), 
                    Div(Field('longitud_acceso_construccion', 
                            css_class='input input-warning w-full',
                            placeholder='ej: 18 / 18 +50 / +100 m',
                            ), css_class=' w-full sm:w-3/4'), 
                    css_class='flex sm:flex-row flex-col justify-between gap-3'
                    ),
                Div(Field('tipo_suelo', css_class='input input-warning w-full'), css_class='max-w-16'),
                Div(Field('obstaculos', css_class='input input-warning w-full'), css_class='max-w-16'),
                Div(Field('adicionales', css_class='input input-warning w-full'), css_class='max-w-16'),
                css_class='flex flex-row justify-between gap-3'
            ),
            # Botón de envío
            Div(
                Submit('submit', 'Guardar Registro', css_class='btn btn-success w-full mt-6 sombra'),
                css_class='text-center'
            ),
        )

    
    class Meta:
        model = RAcceso
        fields = ['registro', 'acceso_sitio', 'acceso_sitio_construccion', 'longitud_acceso_sitio', 'longitud_acceso_construccion', 'tipo_suelo', 'obstaculos', 'adicionales']
        labels = {
            'registro': 'Registro Tx/Tss',
            'acceso_sitio': 'Acceso al sitio',
            'acceso_sitio_construccion': 'Acceso al sitio para construcción',
            'longitud_acceso_sitio': 'Longitud acceso al Sitio',
            'longitud_acceso_construccion': 'Longitud acceso al Sitio para construcción',
            'tipo_suelo': 'Tipo de suelo de sitio y huella',
            'obstaculos': 'Edificaciones cercanas / obstáculos',
            'adicionales': 'Trabajos adicionales a considerar',
        }
