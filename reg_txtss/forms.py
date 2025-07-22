"""
Formularios para registros TX/TSS.
"""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from .models import RSitio, RAcceso, REmpalme, RegTxtss
from registros.forms.utils import get_form_field_css_class, get_field_css_class
from crispy_forms.layout import Layout, Field, Submit, Div, HTML

class RSitioForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.registro_id = kwargs.pop('registro_id', None)
        print(f"DEBUG RSitioForm: registro_id = {self.registro_id}")  # Debug
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'pb-4'
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        # Set help text for fields
        self.fields['lat'].help_text = 'Grados decimales.'
        self.fields['lon'].help_text = 'Grados decimales.'
        self.fields['dimensiones'].help_text = 'Dimensiones del sitio'
        self.fields['altura'].help_text = 'Metros'
        self.fields['deslindes'].help_text = 'Distancia a los bordes de la propiedad, las distancias cortas deben ser precisas.'
        
        # Configurar el campo registro automáticamente
        
        # Configurar el queryset del campo registro
        self.fields['registro'].queryset = RegTxtss.objects.all()
        
        try:
            if self.registro_id:
                # Para formularios nuevos, establecer el registro según el ID
                registro_obj = RegTxtss.objects.get(id=self.registro_id)
                # Primero ocultar el campo (comentado para pruebas)
                # self.fields['registro'].widget = forms.HiddenInput()
                # Luego establecer el valor inicial
                self.initial['registro'] = registro_obj.id  # Usar el ID, no el objeto
                self.fields['registro'].initial = registro_obj.id  # Usar el ID, no el objeto
            elif self.instance.pk:
                # Para formularios existentes, ocultar el campo (comentado para pruebas)
                pass
                # self.fields['registro'].widget = forms.HiddenInput()
            else:
                # Si no hay registro_id, ocultar el campo (comentado para pruebas)
                pass
                # self.fields['registro'].widget = forms.HiddenInput()
        except RegTxtss.DoesNotExist:
            # Si el registro no existe, ocultar el campo (comentado para pruebas)
            pass
            # self.fields['registro'].widget = forms.HiddenInput()

        # HTML for map location button
        btn_ubicar_mapa_html = '''
        <button type="button"
            id="btn-ubicar-mapa"
            class="btn btn-ghost p-0 h-10 m-0 sm:h-12 w-10 sm:w-12 my-auto">
                <svg width="64px" height="64px" viewBox="0 0 1024 1024" class="icon sombra" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M640 213.333333L384 128 128 213.333333v682.666667l256-85.333333 256 85.333333 256-85.333333V128z" fill="#FFECB3"></path><path d="M384 128v682.666667l256 85.333333V213.333333z" fill="#FFE082"></path><path d="M640 320c-82.496 0-149.333333 70.250667-149.333333 156.821333S640 768 640 768s149.333333-204.629333 149.333333-291.178667S722.496 320 640 320z" fill="#F44336"></path><path d="M640 469.333333m-64 0a64 64 0 1 0 128 0 64 64 0 1 0-128 0Z" fill="#FFEBEE"></path></g></svg>
        </button>
        '''
        
        self.helper.layout = Layout(
            Field('registro'),
            Div(
                HTML(btn_ubicar_mapa_html),
                Div(
                    HTML('{% include "registros/forms/lat_lon_input.html" with field=form.lat %}'),
                    HTML('{% include "registros/forms/lat_lon_input.html" with field=form.lon %}'),
                    css_class='flex flex-row justify-between gap-3 mb-3'
                ),
                css_class='flex flex-row justify-between gap-3 mb-3'
            ),
            
            

            Div(
                Field('dimensiones', css_class=f"{get_form_field_css_class(self, 'dimensiones')} w-full"),
                Field('altura', css_class=f"{get_form_field_css_class(self, 'altura')} w-full "),
                css_class='flex sm:flex-row flex-col justify-between gap-3',
            ),
            Div(
                Field('deslindes', css_class=f"{get_form_field_css_class(self, 'deslindes')} w-full"),
                css_class='flex flex-row justify-between gap-3'
            ),
            Div(
                Field('comentarios', css_class=f"{get_form_field_css_class(self, 'comentarios')} w-full"),
                css_class='mb-3'
            ),
            Div(
                Submit('submit', 'Guardar Registro', css_class='btn btn-success w-full mt-4 sombra'),
                css_class='text-center'
            ),
        
        )
    
    class Meta:
        model = RSitio
        fields = ['registro', 'lat', 'lon', 'dimensiones', 'altura', 'deslindes', 'comentarios']
        labels = {
            'lat': 'Latitud',
            'lon': 'Longitud',
            'dimensiones': 'Dimensiones del sitio',
            'altura': 'Altura',
            'deslindes': 'Deslindes',
            'comentarios': 'Comentarios',
        } 

class RAccesoForm(forms.ModelForm):
    """Formulario para el paso Acceso."""
    
    def __init__(self, *args, **kwargs):
        self.registro_id = kwargs.pop('registro_id', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "pb-4"
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        # Configurar el campo registro automáticamente
        try:
            if self.registro_id:
                # Para formularios nuevos, establecer el registro según el ID
                registro_obj = RegTxtss.objects.get(id=self.registro_id)
                self.initial['registro'] = registro_obj.id  # Usar el ID, no el objeto
                self.fields['registro'].widget = forms.HiddenInput()
                self.fields['registro'].initial = registro_obj.id  # Usar el ID, no el objeto
            elif self.instance.pk:
                # Para formularios existentes, ocultar el campo
                self.fields['registro'].widget = forms.HiddenInput()
            else:
                # Si no hay registro_id, ocultar el campo
                self.fields['registro'].widget = forms.HiddenInput()
        except RegTxtss.DoesNotExist:
            # Si el registro no existe, ocultar el campo
            self.fields['registro'].widget = forms.HiddenInput()
        
        self.helper.layout = Layout(
            Field('registro'),
            Field('tipo_suelo', css_class='input input-success sombra'),
            Field('distancia', css_class='input input-success sombra'),
            Field('comentarios', css_class='textarea textarea-warning sombra rows-2'),
            Submit('submit', 'Guardar', css_class='btn btn-primary'),
        )
    
    class Meta:
        model = RAcceso
        fields = ['registro', 'tipo_suelo', 'distancia', 'comentarios']
        widgets = {
            'tipo_suelo': forms.TextInput(attrs={'class': 'input input-success sombra'}),
            'distancia': forms.TextInput(attrs={'class': 'input input-success sombra'}),
            'comentarios': forms.Textarea(attrs={'class': 'textarea textarea-warning sombra rows-2'}),
        }


class REmpalmeForm(forms.ModelForm):
    """Formulario para el paso Empalme."""
    
    def __init__(self, *args, **kwargs):
        self.registro_id = kwargs.pop('registro_id', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "pb-4"
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        # Configurar el campo registro automáticamente
        try:
            if self.registro_id:
                # Para formularios nuevos, establecer el registro según el ID
                registro_obj = RegTxtss.objects.get(id=self.registro_id)
                self.initial['registro'] = registro_obj.id  # Usar el ID, no el objeto
                self.fields['registro'].widget = forms.HiddenInput()
                self.fields['registro'].initial = registro_obj.id  # Usar el ID, no el objeto
            elif self.instance.pk:
                # Para formularios existentes, ocultar el campo
                self.fields['registro'].widget = forms.HiddenInput()
            else:
                # Si no hay registro_id, ocultar el campo
                self.fields['registro'].widget = forms.HiddenInput()
        except RegTxtss.DoesNotExist:
            # Si el registro no existe, ocultar el campo
            self.fields['registro'].widget = forms.HiddenInput()
        
        self.helper.layout = Layout(
            Field('registro'),
            Field('proveedor', css_class='input input-success sombra'),
            Field('capacidad', css_class='input input-success sombra'),
            Field('comentarios', css_class='textarea textarea-warning sombra rows-2'),
            Submit('submit', 'Guardar', css_class='btn btn-primary'),
        )
    
    class Meta:
        model = REmpalme
        fields = ['registro', 'proveedor', 'capacidad', 'comentarios']
        widgets = {
            'proveedor': forms.TextInput(attrs={'class': 'input input-success sombra'}),
            'capacidad': forms.TextInput(attrs={'class': 'input input-success sombra'}),
            'comentarios': forms.Textarea(attrs={'class': 'textarea textarea-warning sombra rows-2'}),
        } 