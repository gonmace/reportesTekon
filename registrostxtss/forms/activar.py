from django import forms
from users.models import User
from registrostxtss.models.registrostxtss import RegistrosTxTss
from crispy_forms.layout import Layout, Submit, Button, Div, Field
from crispy_forms.helper import FormHelper
from core.models.sites import Site

class ActivarRegistroForm(forms.ModelForm):
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
        self.fields['sitio'].queryset = Site.get_actives()
        self.fields['user'].queryset = User.objects.filter(user_type=User.ITO)
    
    class Meta:
        model = RegistrosTxTss
        fields = ['sitio', 'user']