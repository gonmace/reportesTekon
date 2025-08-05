"""
Formularios para registros reg_construccion.
"""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from .models import RegConstruccion, Visita, Avance
from registros.forms.utils import get_form_field_css_class


class VisitaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.registro_id = kwargs.pop('registro_id', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'p-0 md:p-2'
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        # Configurar el campo registro automáticamente
        self.fields['registro'].queryset = RegConstruccion.objects.all()
        
        try:
            if self.registro_id:
                registro_obj = RegConstruccion.objects.get(id=self.registro_id)
                self.fields['registro'].widget = forms.HiddenInput()
                self.initial['registro'] = registro_obj.id
                self.fields['registro'].initial = registro_obj.id
            elif self.instance.pk:
                self.fields['registro'].widget = forms.HiddenInput()
            else:
                self.fields['registro'].widget = forms.HiddenInput()
        except RegConstruccion.DoesNotExist:
            self.fields['registro'].widget = forms.HiddenInput()

        self.helper.layout = Layout(
            Field('registro'),
            Field('comentarios', css_class=f"{get_form_field_css_class(self, 'comentarios')} w-full"),
            Div(
                Submit('submit', 'Guardar Registro', css_class='btn btn-success w-full mt-4 sombra'),
                css_class='text-center'
            ),
        )
    
    class Meta:
        model = Visita
        fields = ['registro', 'comentarios']
        labels = {
            'comentarios': 'Comentarios',
        }
        widgets = {
            'comentarios': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ingrese comentarios...'}),
        }


class AvanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.registro_id = kwargs.pop('registro_id', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'p-0 md:p-2'
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        # Configurar el campo registro automáticamente
        self.fields['registro'].queryset = RegConstruccion.objects.all()
        
        try:
            if self.registro_id:
                registro_obj = RegConstruccion.objects.get(id=self.registro_id)
                self.fields['registro'].widget = forms.HiddenInput()
                self.initial['registro'] = registro_obj.id
                self.fields['registro'].initial = registro_obj.id
            elif self.instance.pk:
                self.fields['registro'].widget = forms.HiddenInput()
            else:
                self.fields['registro'].widget = forms.HiddenInput()
        except RegConstruccion.DoesNotExist:
            self.fields['registro'].widget = forms.HiddenInput()

        self.helper.layout = Layout(
            Field('registro'),
            Field('comentarios', css_class=f"{get_form_field_css_class(self, 'comentarios')} w-full"),
            Div(
                Submit('submit', 'Guardar Registro', css_class='btn btn-success w-full mt-4 sombra'),
                css_class='text-center'
            ),
        )
    
    class Meta:
        model = Avance
        fields = ['registro', 'comentarios']
        labels = {
            'comentarios': 'Comentarios',
        }
        widgets = {
            'comentarios': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ingrese comentarios...'}),
        }

