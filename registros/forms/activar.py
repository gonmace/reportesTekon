from django import forms
from users.models import User
from crispy_forms.layout import Layout, Submit, Button, Div, Field
from crispy_forms.helper import FormHelper
from core.models.sites import Site
from registros.models.base import RegistroBase


def create_activar_registro_form(registro_model, title_default='Registro', description_default='Registro activado desde el formulario'):
    """
    Factory function para crear un formulario de activación específico para un modelo.
    
    Args:
        registro_model: Clase del modelo que hereda de RegistroBase
        title_default: Título por defecto
        description_default: Descripción por defecto
    
    Returns:
        Clase de formulario configurada
    """
    class ActivarRegistroForm(forms.ModelForm):
        """
        Formulario para activar registros.
        """
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            self.helper = FormHelper()
            self.helper.form_tag = True
            self.helper.form_method = 'post'
            self.helper.form_action = ''
            self.helper.label_class = 'text-sm text-base-content'
            self.helper.field_class = 'mb-2'
            self.helper.layout = Layout(
                Div(
                    Div(Field('sitio', css_class='select  w-full'), css_class='w-full'),
                    Div(Field('user', css_class='select w-full'), css_class='w-full'),
                    css_class='flex flex-wrap -mx-2 mb-4',
                ),
                Div(
                    Button('cancel', 'Cancelar', css_class='btn btn-error mt-6', type='button', onclick='closeModal()'),
                    Submit('submit', 'Activar Registro', css_class='btn btn-success flex-grow mt-6', css_id='activar-registro-btn'),
                    css_class='flex gap-2 justify-center',
                ),
            )
            
            # Configurar campos ocultos
            if 'title' in self.fields:
                self.fields['title'].widget = forms.HiddenInput()
            if 'description' in self.fields:
                self.fields['description'].widget = forms.HiddenInput()
            
            self.fields['sitio'].queryset = Site.get_actives()
            self.fields['user'].queryset = User.objects.filter(user_type=User.ITO)
            
            # Establecer valores por defecto
            if not self.instance.pk:
                if 'title' in self.fields:
                    self.fields['title'].initial = title_default
                if 'description' in self.fields:
                    self.fields['description'].initial = description_default
        
        class Meta:
            model = registro_model
            fields = ['sitio', 'user', 'title', 'description']
    
    return ActivarRegistroForm