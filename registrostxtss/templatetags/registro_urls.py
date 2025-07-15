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
        'form': f'registrostxtss:r_{etapa}',
        'photos': f'registrostxtss:photos_{etapa}',
        'edit': f'registrostxtss:edit_{etapa}',
        'delete': f'registrostxtss:delete_{etapa}',
        'view': f'registrostxtss:view_{etapa}',
    }
    
    try:
        # Intentar generar la URL usando el patrón específico
        url_name = url_patterns.get(tipo, f'registrostxtss:{tipo}_{etapa}')
        return reverse(url_name, kwargs={'registro_id': registro_id})
    except NoReverseMatch:
        # Si no existe la URL específica, usar el patrón genérico
        if tipo == 'photos':
            return f'/registrostxtss/{registro_id}/{etapa}/photos/'
        else:
            return f'/registrostxtss/{registro_id}/{etapa}/'

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