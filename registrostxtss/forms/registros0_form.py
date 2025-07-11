from django import forms
from registrostxtss.models.registros_model import Registros0
from registrostxtss.models.status_registros_model import RegistrosTxTss
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from crispy_forms.layout import HTML
from django.conf import settings

if settings.DEBUG:
    from rich.console import Console
    console = Console()


class Registros0Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Extraer registroId de los argumentos si está presente
        self.registro_id = kwargs.pop('registro_id', None)
        console.print(f"ahi esta el registro_id: {self.registro_id}", style="bold red")

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = "pb-4"
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
              
        # Si se proporciona registro_id, pre-seleccionar el registro correspondiente
        if self.registro_id and not self.instance.pk:
            registro_obj = RegistrosTxTss.objects.get(id=self.registro_id)
            sitio = registro_obj.sitio
            self.initial['registro'] = registro_obj
            self.fields['registro'].widget = forms.HiddenInput()
            # Solo establecer altura si existe el campo alt en el sitio
            if hasattr(sitio, 'alt') and sitio.alt:
                self.initial['altura'] = sitio.alt 

      
                # HTML dinámico
        header_html = f"""
        <div class="bg-base-200 p-4 rounded-t-lg pb-1">
            <h2>{sitio.pti_cell_id or ''}</h2>
            <h3 class="text-sm font-semibold mb-3">{sitio.operator_id or ''} - {sitio.name or '__'}</h3>
        </div>
        """
            
        self.helper.layout = Layout(
            HTML(header_html),
            Field('registro'),
            HTML("""
    <div class="w-full px-2 mb-2">
        <button type="button"
                id="btn-ubicar-mapa"
                class="btn btn-warning" ">
            <i class="fa-solid fa-map-location-dot"></i>
        </button>
    </div>
    <script>
        function asignarLatitudAleatoria() {
            const latInput = document.getElementById('id_lat');
            if (latInput) {
                const lat = (Math.random() * -90).toFixed(7);  // latitud negativa para hemisferio sur
                latInput.value = lat;
            }
        }
    </script>
    """),
            Div(
                Div(Field('lat', css_class='input input-bordered w-full'), css_class='w-1/2 px-2'),
                Div(Field('lon', css_class='input input-bordered w-full'), css_class='w-1/2 px-2'),
                css_class='flex flex-wrap -mx-2 mb-4',
            ),
            # Altura
            Div(
                Field('altura', css_class='input input-bordered w-full'),
                css_class='mb-4'
            ),
            # Dimensiones y deslindes
            Div(
                Div(Field('dimensiones', css_class='input input-bordered w-full'), css_class='w-1/2 px-2'),
                Div(Field('deslindes', css_class='input input-bordered w-full'), css_class='w-1/2 px-2'),
                css_class='flex flex-wrap -mx-2 mb-4',
            ),
            # Botón de envío
            Div(
                Submit('submit', 'Guardar Registro', css_class='btn btn-success w-full mt-6'),
                css_class='text-center'
            ),
        )

    
    class Meta:
        model = Registros0
        fields = ['registro', 'lat', 'lon', 'altura', 'dimensiones', 'deslindes']
        labels = {
            'registro': 'Registro Tx/Tss',
            'lat': 'Latitud Inspección',
            'lon': 'Longitud Inspección',
            'altura': 'Altura (m)',
            'dimensiones': 'Dimensiones',
            'deslindes': 'Deslindes',
        }
