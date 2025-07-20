"""
Funciones para verificar la completitud de modelos.
"""

from django.db import models
from typing import Dict, Any, List


def check_model_completeness(model_class, instance_id: int) -> Dict[str, Any]:
    """
    Verifica la completitud de un modelo basado en sus campos.
    
    Args:
        model_class: Clase del modelo a verificar
        instance_id: ID de la instancia a verificar
        
    Returns:
        Dict con información de completitud
    """
    try:
        instance = model_class.objects.get(id=instance_id)
    except model_class.DoesNotExist:
        return {
            'color': 'gray',
            'is_complete': False,
            'missing_fields': [],
            'total_fields': 0,
            'filled_fields': 0,
            'percentage': 0
        }
    
    # Obtener campos del modelo (excluyendo campos automáticos)
    fields = model_class._meta.get_fields()
    field_names = []
    
    for field in fields:
        # Excluir campos automáticos y relaciones
        if (isinstance(field, models.Field) and 
            not field.auto_created and 
            not field.is_relation and
            field.name not in ['id', 'created_at', 'updated_at', 'is_deleted']):
            field_names.append(field.name)
    
    total_fields = len(field_names)
    filled_fields = 0
    missing_fields = []
    
    for field_name in field_names:
        value = getattr(instance, field_name, None)
        if value is not None and value != '':
            filled_fields += 1
        else:
            missing_fields.append(field_name)
    
    # Calcular porcentaje
    percentage = (filled_fields / total_fields * 100) if total_fields > 0 else 0
    
    # Determinar color basado en completitud
    if percentage == 100:
        color = 'green'
        is_complete = True
    elif percentage >= 75:
        color = 'yellow'
        is_complete = False
    elif percentage >= 50:
        color = 'orange'
        is_complete = False
    else:
        color = 'red'
        is_complete = False
    
    return {
        'color': color,
        'is_complete': is_complete,
        'missing_fields': missing_fields,
        'total_fields': total_fields,
        'filled_fields': filled_fields,
        'percentage': round(percentage, 1)
    } 