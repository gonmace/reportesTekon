from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.simple_tag
def get_registro_url(etapa, registro_id, tipo='form'):
    """
    Genera la URL para cualquier tipo de vista relacionada con registros.
    
    Args:
        etapa: Nombre de la etapa (sitio, acceso, etc.)
        registro_id: ID del registro
        tipo: Tipo de URL ('form', 'photos', 'edit', etc.)
        
    Returns:
        URL generada o URL por defecto si no existe
    """
    # Mapeo de tipos de URL a patrones de nombres
    url_patterns = {
        'form': f'registros_txtss:r_{etapa}',
        'photos': f'photos:list',
        'edit': f'registros_txtss:edit_{etapa}',
        'delete': f'registros_txtss:delete_{etapa}',
        'view': f'registros_txtss:view_{etapa}',
    }
    
    try:
        # Intentar generar la URL usando el patrón específico
        url_name = url_patterns.get(tipo, f'registros_txtss:{tipo}_{etapa}')
        if tipo == 'photos':
            return reverse(url_name, kwargs={'registro_id': registro_id, 'title': etapa})
        else:
            return reverse(url_name, kwargs={'registro_id': registro_id})
    except NoReverseMatch:
        # Si no existe la URL específica, usar el patrón genérico
        if tipo == 'photos':
            return f'/txtss/registros/{registro_id}/{etapa}/photos/'
        else:
            return f'/txtss/registros/{registro_id}/{etapa}/'

@register.simple_tag
def get_registro_photos_url(etapa, registro_id):
    """
    Genera la URL para las fotos de una etapa específica de registro.
    
    Args:
        etapa: Nombre de la etapa (sitio, acceso, etc.)
        registro_id: ID del registro
        
    Returns:
        URL generada para las fotos
    """
    return get_registro_url(etapa, registro_id, 'photos') 