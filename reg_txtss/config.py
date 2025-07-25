"""
Configuración declarativa para registros TX/TSS.
"""
# Rojo	    rgb(255, 64, 64)	#FF4040	0xFF4040
# Amarillo	rgb(255, 255, 68)	#FFFF44	0xFFFF44
# Azul     	rgb(0, 84, 255)	    #0054FF	0x0054FF
# Cyan 	    rgb(87, 247, 247)	#57F7F7	0x57F7F7

from registros.config import (
    create_simple_config, 
    create_registro_config,
    create_1_point_map_config,
    create_2_point_map_config,
    create_3_point_map_config,
    create_photos_config,
    create_custom_config,
    create_sub_element_only_config
)
from .models import RegTxtss, RSitio, RAcceso, REmpalme
from .forms import RSitioForm, RAccesoForm, REmpalmeForm
from core.models.sites import Site

mandato_map = create_1_point_map_config(
    model_class1=Site,
    lat1='lat_base',
    lon1='lon_base',
    name1='Mandato',
    icon1_color='#0054FF',
)


sitio_mapa_component = create_2_point_map_config(
    model_class1='current',
    lat1='lat',
    lon1='lon', 
    name1='Inspección',
    icon1_color='#FFFF44',
    icon1_size='mid',
    icon1_type='marker',
    model_class2=Site,
    lat2='lat_base',
    lon2='lon_base', 
    name2='Mandato',
    second_model_relation_field='sitio',
    descripcion_distancia='Desfase Mandato-Inspección',
    icon2_color='#0054FF',
    icon2_size='normal',
    icon2_type='marker',
    zoom=15,
    template_name='components/mapa_modal.html',
    distancia=True,
    template_datos_clave='components/datos_clave_sitio.html',
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

# Crear componente de mapa de 3 puntos para el paso 'empalme'
empalme_mapa_component = create_3_point_map_config(
    model_class1='current',
    lat1='lat',
    lon1='lon', 
    name1='Empalme',
    icon1_color='#FF4040',
    icon1_size='mid',
    icon1_type='marker',
    
    model_class2=RSitio,
    lat2='lat',
    lon2='lon', 
    name2='Inspección',
    second_model_relation_field='registro',
    icon2_color='#FFFF44',
    icon2_size='normal',
    icon2_type='marker',
    
    model_class3=Site,
    lat3='lat_base',
    lon3='lon_base', 
    name3='Mandato',
    third_model_relation_field='sitio',
    descripcion_distancia='Distancia entre puntos',
    icon3_color='#0054FF',
    icon3_size='tiny',
    icon3_type='marker',
    
    zoom=15,
    template_name='components/mapa_modal.html',
    distancia=True,
    template_datos_clave='components/datos_clave_empalme.html',
)

# Configuración de pasos usando create_custom_config con componentes personalizados
PASOS_CONFIG = {
    'mandato': create_sub_element_only_config(
        title='Mandato',
        description='Información sobre el mandato.',
        sub_elementos=[mandato_map]
    ),
    'sitio': create_custom_config(
        model_class=RSitio,
        form_class=RSitioForm,
        title='Sitio',
        description='Información general del sitio.',
        template_form='components/elemento_form.html',
        sub_elementos=[sitio_mapa_component, sitio_fotos_component]
    ),
    
    'acceso': create_custom_config(
        model_class=RAcceso,
        form_class=RAccesoForm,
        title='Acceso',
        description='Información sobre el acceso al sitio.',
        template_form='components/elemento_form.html'
    ),
    
    'empalme': create_custom_config(
        model_class=REmpalme,
        form_class=REmpalmeForm,
        title='Empalme',
        description='Información sobre el empalme.',
        sub_elementos=[empalme_mapa_component, empalme_fotos_component]
    ),
}

# Configuración completa del registro
REGISTRO_CONFIG = create_registro_config(
    registro_model=RegTxtss,
    pasos_config=PASOS_CONFIG,
    title='TX/TSS',
    app_namespace='reg_txtss',
    list_template='components/generic_tables2_template.html',
    steps_template='pages/steps_generic.html'
) 