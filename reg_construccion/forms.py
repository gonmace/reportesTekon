"""
Formularios para registros Reporte de construcción.
"""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from .models import RegConstruccion, Visita, Avance, AvanceComponente
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
            Field('fecha', css_class=f"{get_form_field_css_class(self, 'fecha')} w-full"),
            Field('porcentaje_avance', css_class=f"{get_form_field_css_class(self, 'porcentaje_avance')} w-full"),
            Field('comentarios', css_class=f"{get_form_field_css_class(self, 'comentarios')} w-full"),
            Div(
                Submit('submit', 'Guardar Avance', css_class='btn btn-success w-full mt-4 sombra'),
                css_class='text-center'
            ),
        )
    
    class Meta:
        model = Avance
        fields = ['registro', 'fecha', 'porcentaje_avance', 'comentarios']
        labels = {
            'fecha': 'Fecha del avance',
            'porcentaje_avance': 'Porcentaje de avance (%)',
            'comentarios': 'Comentarios',
        }
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'porcentaje_avance': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 1}),
            'comentarios': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ingrese comentarios sobre el avance...'}),
        }


class AvanceComponenteForm(forms.ModelForm):
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
        
        # Filtrar componentes según la estructura del proyecto
        if self.registro_id:
            try:
                registro_obj = RegConstruccion.objects.get(id=self.registro_id)
                if registro_obj.estructura:
                    # Obtener componentes de la estructura seleccionada
                    componentes_disponibles = registro_obj.estructura.componentes_grupo.filter(
                        activo=True
                    ).values_list('componente', flat=True)
                    self.fields['componente'].queryset = Componente.objects.filter(
                        id__in=componentes_disponibles
                    ).order_by('nombre')
                else:
                    # Si no hay estructura, mostrar todos los componentes
                    self.fields['componente'].queryset = Componente.objects.all().order_by('nombre')
            except RegConstruccion.DoesNotExist:
                self.fields['componente'].queryset = Componente.objects.all().order_by('nombre')
        
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
            Field('componente', css_class=f"{get_form_field_css_class(self, 'componente')} w-full"),
            Field('fecha', css_class=f"{get_form_field_css_class(self, 'fecha')} w-full"),
            Field('porcentaje_actual', css_class=f"{get_form_field_css_class(self, 'porcentaje_actual')} w-full"),
            Field('porcentaje_acumulado', css_class=f"{get_form_field_css_class(self, 'porcentaje_acumulado')} w-full"),
            Field('comentarios', css_class=f"{get_form_field_css_class(self, 'comentarios')} w-full"),
            Div(
                Submit('submit', 'Guardar Avance por Componente', css_class='btn btn-success w-full mt-4 sombra'),
                css_class='text-center'
            ),
        )
    
    class Meta:
        model = AvanceComponente
        fields = ['registro', 'componente', 'fecha', 'porcentaje_actual', 'porcentaje_acumulado', 'comentarios']
        labels = {
            'componente': 'Componente',
            'fecha': 'Fecha del avance',
            'porcentaje_actual': 'Porcentaje actual (%)',
            'porcentaje_acumulado': 'Porcentaje acumulado (%)',
            'comentarios': 'Comentarios',
        }
        widgets = {
            'componente': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'porcentaje_actual': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 1}),
            'porcentaje_acumulado': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 1}),
            'comentarios': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ingrese comentarios sobre el avance del componente...'}),
        }

