from django import forms
from registrostxtss.r_acceso.models import RAcceso
from registrostxtss.models.registrostxtss import RegistrosTxTss
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
from registrostxtss.forms.utils import get_form_field_css_class


class RAccesoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Extraer registroId de los argumentos si está presente
        self.registro_id = kwargs.pop('registro_id', None)

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = "pb-4"
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        # Configurar help_text para campos específicos
        self.fields['acceso_sitio'].help_text = 'Descripción del acceso al sitio'
        self.fields['acceso_sitio_construccion'].help_text = 'Descripción del acceso para construcción'
        self.fields['longitud_acceso_sitio'].help_text = 'Metros'
        self.fields['longitud_acceso_construccion'].help_text = 'Metros'
        self.fields['tipo_suelo'].help_text = 'Tipo de suelo del sitio y huella'
        self.fields['obstaculos'].help_text = 'Edificaciones cercanas u obstáculos'
        self.fields['adicionales'].help_text = 'Trabajos adicionales a considerar'
        
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
            
        self.helper.layout = Layout(
            Field('registro'),
            Div(
                Div(Field('acceso_sitio', css_class=get_form_field_css_class(self, 'acceso_sitio')), css_class='w-full'),
                css_class='mb-3'
            ),
            Div(
                Div(Field('acceso_sitio_construccion', css_class=get_form_field_css_class(self, 'acceso_sitio_construccion')), css_class='w-full'),
                css_class='mb-3'
            ),
            Div(
                Div(Field('longitud_acceso_sitio', css_class=get_form_field_css_class(self, 'longitud_acceso_sitio')), css_class='w-1/2'),
                Div(Field('longitud_acceso_construccion', css_class=get_form_field_css_class(self, 'longitud_acceso_construccion')), css_class='w-1/2'),
                css_class='flex gap-3 mb-3'
            ),
            Div(
                Div(Field('tipo_suelo', css_class=get_form_field_css_class(self, 'tipo_suelo')), css_class='w-full'),
                css_class='mb-3'
            ),
            Div(
                Div(Field('obstaculos', css_class=get_form_field_css_class(self, 'obstaculos')), css_class='w-full'),
                css_class='mb-3'
            ),
            Div(
                Div(Field('adicionales', css_class=get_form_field_css_class(self, 'adicionales')), css_class='w-full'),
                css_class='mb-3'
            ),
            # Botón de envío
            Div(
                Submit('submit', 'Guardar Registro', css_class='btn btn-success w-full mt-6 sombra'),
                css_class='text-center'
            ),
        )

    class Meta:
        model = RAcceso
        fields = [
            'registro', 'acceso_sitio', 'acceso_sitio_construccion', 
            'longitud_acceso_sitio', 'longitud_acceso_construccion', 
            'tipo_suelo', 'obstaculos', 'adicionales'
        ]
        labels = {
            # 'registro': 'Registro Tx/Tss',
            'acceso_sitio': 'Acceso al sitio',
            'acceso_sitio_construccion': 'Acceso para construcción',
            'longitud_acceso_sitio': 'Longitud acceso al Sitio',
            'longitud_acceso_construccion': 'Longitud acceso para construcción',
            'tipo_suelo': 'Tipo de suelo de sitio y huella',
            'obstaculos': 'Edificaciones cercanas / obstáculos',
            'adicionales': 'Trabajos adicionales a considerar',
        }
