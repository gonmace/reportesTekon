from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from crispy_tailwind.layout import Submit, Reset
from .models.registro import Registros


class RegistroInicialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "bg-base-100 p-6 rounded-lg shadow-lg"
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        self.helper.layout = Layout(
            Field('sitio', css_class='select select-bordered w-full'),
            Field('fecha', css_class='input input-bordered w-full'),
            Field('descripcion', css_class='textarea textarea-bordered w-full', rows=2),
            Submit('submit', 'Guardar Registro', css_class='btn btn-accent w-full mt-6')
        )
    
    class Meta:
        model = Registros
        fields = ['sitio', 'registro0', 'registro1', 'registro2']

