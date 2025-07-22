"""
Configuración declarativa para registros TX/TSS.
"""

from registros.config import (
    create_simple_config, 
    create_registro_config,
    create_multi_point_map_config,
    create_photos_config,
    create_custom_config
)
from .models import RegTxtss, RSitio, RAcceso, REmpalme
from .forms import RSitioForm, RAccesoForm, REmpalmeForm
from core.models.sites import Site


# Crear componentes personalizados para el paso 'sitio'
# Configuración de mapa multi-punto (máximo 3 coordenadas):
# - coord1: Punto de inspección (RSitio)
# - coord2: Punto de mandato (Site)
# - coord3: Futuras expansiones
sitio_mapa_component = create_multi_point_map_config(
    model_class1='current',
    lat1='lat',
    lon1='lon', 
    name1='Inspección',
    icon1_color='red',
    icon1_size='large',
    icon1_type='marker',
    model_class2=Site,
    lat2='lat_base',
    lon2='lon_base', 
    name2='Mandato',
    second_model_relation_field='sitio',
    descripcion_distancia='Desfase Mandato-Inspección',
    icon2_color='blue',
    icon2_size='normal',
    icon2_type='marker',
    zoom=15,
    template_name='components/mapa_modal.html',
)

sitio_fotos_component = create_photos_config(
    photo_min=4,
    photos_template='photos/photos_main.html'
)

# Crear componente de fotos personalizado para el paso 'empalme'
empalme_fotos_component = create_photos_config(
    photo_min=2,
    photos_template='photos/photos_main.html'
)

# Configuración de pasos usando create_custom_config con componentes personalizados
PASOS_CONFIG = {
    'sitio': create_custom_config(
        model_class=RSitio,
        form_class=RSitioForm,
        title='Sitio',
        description='Información general del sitio.',
        template_form='components/elemento_form.html',
        sub_elementos=[sitio_mapa_component, sitio_fotos_component]
    ),
    
    'acceso': create_simple_config(
        model_class=RAcceso,
        form_class=RAccesoForm,
        title='Acceso',
        description='Información sobre el acceso al sitio.'
    ),
    
    'empalme': create_custom_config(
        model_class=REmpalme,
        form_class=REmpalmeForm,
        title='Empalme',
        description='Información sobre el empalme.',
        sub_elementos=[empalme_fotos_component]
    ),
}

# Configuración completa del registro
REGISTRO_CONFIG = create_registro_config(
    registro_model=RegTxtss,
    pasos_config=PASOS_CONFIG,
    title='TX/TSS',
    app_namespace='reg_txtss',
    list_template='pages/main_txtss.html',
    steps_template='pages/steps_txtss.html'
) 