from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, Row, Column
from reg_visita.models import AvanceProyecto, RegVisita
from proyectos.models import EstructuraProyecto, Componente
from core.models.sites import Site


class AvanceFisicoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.sitio_id = kwargs.pop('sitio_id', None)
        self.estructura_id = kwargs.pop('estructura_id', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'p-0 md:p-2'
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        # Configurar el campo registro
        self.fields['registro'].queryset = RegVisita.objects.all()
        
        # Si se proporciona sitio_id, filtrar registros por sitio
        if self.sitio_id:
            try:
                sitio = Site.objects.get(id=self.sitio_id)
                self.fields['registro'].queryset = RegVisita.objects.filter(sitio=sitio)
                # Si solo hay un registro para este sitio, seleccionarlo automáticamente
                if self.fields['registro'].queryset.count() == 1:
                    registro = self.fields['registro'].queryset.first()
                    self.initial['registro'] = registro.id
            except Site.DoesNotExist:
                pass
        
        # Configurar el campo proyecto (estructura)
        self.fields['proyecto'].queryset = EstructuraProyecto.objects.filter(activo=True)
        
        # Si se proporciona estructura_id, seleccionarla automáticamente
        if self.estructura_id:
            try:
                estructura = EstructuraProyecto.objects.get(id=self.estructura_id)
                self.initial['proyecto'] = estructura.id
                # También establecer el componente automáticamente
                self.initial['componente'] = estructura.componente.id
            except EstructuraProyecto.DoesNotExist:
                pass
        
        # Configurar el campo componente
        self.fields['componente'].queryset = Componente.objects.filter(activo=True)

        self.helper.layout = Layout(
            Row(
                Column('registro', css_class='form-group col-md-6'),
                Column('proyecto', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('componente', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Field('comentarios', css_class='w-full'),
            Row(
                Column('ejecucion_anterior', css_class='form-group col-md-3'),
                Column('ejecucion_actual', css_class='form-group col-md-3'),
                Column('ejecucion_acumulada', css_class='form-group col-md-3'),
                Column('ejecucion_total', css_class='form-group col-md-3'),
                css_class='form-row'
            ),
            Div(
                Submit('submit', 'Guardar Avance Físico', css_class='btn btn-success w-full mt-4'),
                css_class='text-center'
            ),
        )
    
    class Meta:
        model = AvanceProyecto
        fields = ['registro', 'proyecto', 'componente', 'comentarios', 'ejecucion_anterior', 'ejecucion_actual', 'ejecucion_acumulada', 'ejecucion_total']
        labels = {
            'registro': 'Registro de Visita',
            'proyecto': 'Estructura de Proyecto',
            'componente': 'Componente',
            'comentarios': 'Comentarios',
            'ejecucion_anterior': '% Ejecución Anterior',
            'ejecucion_actual': '% Ejecución Actual',
            'ejecucion_acumulada': '% Ejecución Acumulada',
            'ejecucion_total': '% Ejecución Total',
        }
        widgets = {
            'comentarios': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Ingrese comentarios sobre el avance del proyecto...'
            }),
            'ejecucion_anterior': forms.NumberInput(attrs={
                'min': 0, 'max': 100, 'step': 0.01,
                'placeholder': '0.00'
            }),
            'ejecucion_actual': forms.NumberInput(attrs={
                'min': 0, 'max': 100, 'step': 0.01,
                'placeholder': '0.00'
            }),
            'ejecucion_acumulada': forms.NumberInput(attrs={
                'min': 0, 'step': 0.01,
                'placeholder': '0.00'
            }),
            'ejecucion_total': forms.NumberInput(attrs={
                'min': 0, 'step': 0.01,
                'placeholder': '0.00'
            }),
        } 