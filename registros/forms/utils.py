def get_field_css_class(field, field_name=None, base_class='input sombra'):
    """
    Determina la clase CSS para un campo basado en si es requerido o no.
    
    Args:
        field: El campo del formulario
        field_name: Nombre del campo (opcional, para casos especiales)
        base_class: Clase base para el campo (por defecto 'input sombra')
    
    Returns:
        str: Clase CSS completa para el campo
    """
    # Verificar si el campo es requerido
    is_required = field.required
    
    # Determinar el tipo de widget
    widget_type = type(field.widget).__name__.lower()
    
    # Clase base según el tipo de widget
    if 'textarea' in widget_type:
        base_class = 'textarea sombra'
        if is_required:
            css_class = f'{base_class} textarea-success rows-2 sombra'
        else:
            css_class = f'{base_class} textarea-warning rows-2 sombra'

    else:
        # Para inputs de texto, número, email, etc.
        if is_required:
            css_class = f'{base_class} input-success sombra'
        else:
            css_class = f'{base_class} input-warning sombra'
    
    # Agregar clases específicas según el nombre del campo (opcional)
    if field_name:
        css_class = add_field_specific_classes(css_class, field_name)
    
    return css_class


def get_form_field_css_class(form, field_name, base_class='input sombra'):
    """
    Versión simplificada que toma el formulario y el nombre del campo.
    
    Args:
        form: Instancia del formulario
        field_name: Nombre del campo
        base_class: Clase base para el campo
    
    Returns:
        str: Clase CSS completa para el campo
    """
    field = form.fields[field_name]
    return get_field_css_class(field, field_name, base_class)


def add_field_specific_classes(css_class, field_name):
    """
    Agrega clases específicas según el nombre del campo.
    Esta función es opcional y se puede personalizar según necesidades específicas.
    
    Args:
        css_class: Clase CSS base
        field_name: Nombre del campo
    
    Returns:
        str: Clase CSS con clases específicas agregadas
    """
    # Clases específicas por nombre de campo (opcional)
    specific_classes = {
        # Campos que necesitan altura específica
        'acceso_sitio': 'rows-2',
        'acceso_sitio_construccion': 'rows-2',
        'comentarios': 'rows-2',
        'descripcion': 'rows-2',
        'mensaje': 'rows-2',
        'notas': 'rows-2',
        
        # Campos que necesitan ancho completo
        'longitud_acceso_sitio': 'w-full',
        'longitud_acceso_construccion': 'w-full',
        'tipo_suelo': 'w-full',
        'lat': 'w-full',
        'lon': 'w-full',
        'altura': 'w-full',
        'dimensiones': 'w-full',
        'deslindes': 'w-full',
        'nombre': 'w-full',
        'email': 'w-full',
        'titulo': 'w-full',
        'subtitulo': 'w-full',
    }
    
    # Agregar clase específica si existe
    if field_name in specific_classes:
        css_class += f' {specific_classes[field_name]}'
    
    return css_class


def get_field_css_class_simple(field, base_class='input sombra'):
    """
    Versión simplificada que solo considera si el campo es requerido,
    sin clases específicas por nombre de campo.
    
    Args:
        field: El campo del formulario
        base_class: Clase base para el campo
    
    Returns:
        str: Clase CSS básica para el campo
    """
    return get_field_css_class(field, field_name=None, base_class=base_class)


def get_form_field_css_class_simple(form, field_name, base_class='input sombra'):
    """
    Versión simplificada que no agrega clases específicas por nombre de campo.
    
    Args:
        form: Instancia del formulario
        field_name: Nombre del campo
        base_class: Clase base para el campo
    
    Returns:
        str: Clase CSS básica para el campo
    """
    field = form.fields[field_name]
    return get_field_css_class_simple(field, base_class) 