"""
Configuración genérica para aplicaciones de registros.
"""

from registros.components.registro_config import RegistroConfig, PasoConfig, ElementoConfig, SubElementoConfig
from typing import Dict, Any, Type
from django.db import models
from photos.views import set_photos_template_for_step



def create_photo_map_config(
    model_class: Type[models.Model],
    form_class: Type,
    title: str,
    description: str,
    photo_min: int = 4,
    template_form: str = 'components/elemento_form.html',
    photos_template: str = 'photos/photos_main.html'
) -> PasoConfig:
    """
    Crea una configuración de paso para sitio con mapa y fotos.
    
    Args:
        model_class: Clase del modelo del paso
        form_class: Clase del formulario
        title: Título del paso
        description: Descripción del paso
        photo_min: Número mínimo de fotos requeridas
        template_form: Template para el formulario
        photos_template: Template para las fotos
    
    Returns:
        PasoConfig configurado
    """
    # Configurar el template de ListPhotosView dinámicamente
    set_photos_template_for_step(title.lower(), photos_template)
    return PasoConfig(
        elemento=ElementoConfig(
            nombre='sitio',
            model=model_class,
            form_class=form_class,
            title=title,
            description=description,
            template_name=template_form,
            success_message="Datos del sitio guardados exitosamente.",
            error_message="Error al guardar los datos del sitio.",
            sub_elementos=[
                SubElementoConfig(
                    tipo='mapa',
                    config={
                        'lat_field': 'lat',
                        'lon_field': 'lon',
                        'zoom': 15
                    },
                    template_name='components/mapa.html',
                    css_classes='mapa-container'
                ),
                SubElementoConfig(
                    tipo='fotos',
                    config={
                        'min_files': photo_min,
                        'allowed_types': ['image/jpeg', 'image/png']
                    },
                    template_name=photos_template,
                    css_classes='fotos-container'
                )
            ]
        ),
        title=title,
        description=description
    )


def create_photo_config(
    model_class: Type[models.Model],
    form_class: Type,
    title: str,
    description: str,
    photo_min: int = 4,
    photos_template: str = 'photos/photos_main.html'
) -> PasoConfig:
    """
    Crea una configuración de paso simple con fotos.
    
    Args:
        model_class: Clase del modelo del paso
        form_class: Clase del formulario
        title: Título del paso
        description: Descripción del paso
        photo_min: Número mínimo de fotos requeridas
        photos_template: Template para las fotos
    
    Returns:
        PasoConfig configurado
    """
    # Configurar el template de ListPhotosView dinámicamente
    set_photos_template_for_step(title.lower(), photos_template)
    return PasoConfig(
        elemento=ElementoConfig(
            nombre=title.lower(),
            model=model_class,
            form_class=form_class,
            title=title,
            description=description,
            success_message=f"Datos de {title.lower()} guardados exitosamente.",
            error_message=f"Error al guardar los datos de {title.lower()}.",
            sub_elementos=[
                SubElementoConfig(
                    tipo='fotos',
                    config={
                        'min_files': photo_min,
                        'allowed_types': ['image/jpeg', 'image/png']
                    },
                    template_name=photos_template,
                    css_classes='fotos-container'
                )
            ]
        ),
        title=title,
        description=description
    )


def create_simple_config(
    model_class: Type[models.Model],
    form_class: Type,
    title: str,
    description: str
) -> PasoConfig:
    """
    Crea una configuración de paso simple solo con formulario.
    
    Args:
        model_class: Clase del modelo del paso
        form_class: Clase del formulario
        title: Título del paso
        description: Descripción del paso
    
    Returns:
        PasoConfig configurado
    """
    return PasoConfig(
        elemento=ElementoConfig(
            nombre=title.lower(),
            model=model_class,
            form_class=form_class,
            title=title,
            description=description,
            success_message=f"Datos de {title.lower()} guardados exitosamente.",
            error_message=f"Error al guardar los datos de {title.lower()}."
        ),
        title=title,
        description=description
    )


def create_registro_config(
    registro_model: Type[models.Model],
    pasos_config: Dict[str, PasoConfig],
    title: str,
    app_namespace: str,
    list_template: str = "pages/main_generic.html",
    steps_template: str = "pages/steps_generic.html",
    header_title: str = None
) -> RegistroConfig:
    """
    Crea una configuración completa de registro.
    
    Args:
        registro_model: Modelo principal del registro
        pasos_config: Diccionario con la configuración de pasos
        title: Título de la aplicación
        app_namespace: Namespace de la aplicación
        list_template: Template para listar registros
        steps_template: Template para mostrar pasos
    
    Returns:
        RegistroConfig configurado
    """
    return RegistroConfig(
        registro_model=registro_model,
        pasos=pasos_config,
        list_template=list_template,
        steps_template=steps_template,
        title=title,
        app_namespace=app_namespace,
        breadcrumbs=[
            {'label': 'Inicio', 'url_name': 'dashboard:dashboard'},
            {'label': title}
        ],
        header_title=header_title
    ) 