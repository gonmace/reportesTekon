from typing import Dict, List, Any, Type
from django.db import models


class CompletenessChecker:
    """
    Clase genérica para verificar la completitud de registros en modelos Django.
    Verifica si todos los campos obligatorios están llenos.
    """
    
    @staticmethod
    def check_completeness(model_class: Type[models.Model], instance_id: int) -> Dict[str, Any]:
        """
        Verifica si un registro tiene todos los campos obligatorios llenos.
        Solo verifica campos que no tienen blank=True y null=True.
        
        Args:
            model_class: Clase del modelo Django
            instance_id: ID del registro a verificar
            
        Returns:
            dict: Diccionario con información sobre la completitud del registro
                {
                    'color': str,
                    'is_complete': bool,
                    'missing_fields': list,
                    'total_fields': int,
                    'filled_fields': int
                }
        """
        # Obtener la instancia del modelo por ID
        try:
            instance = model_class.objects.get(id=instance_id)
        except model_class.DoesNotExist:
            return {
                'color': 'error',
                'is_complete': None,
                'missing_fields': [f'{model_class.__name__.lower()}_no_encontrado'],
                'total_fields': 0,
                'filled_fields': 0
            }
        
        missing_fields = []
        
        # Obtener todos los campos del modelo
        fields = instance._meta.get_fields()
        
        for field in fields:
            # Solo verificar campos que no son automáticos y no tienen blank=True y null=True
            if (hasattr(field, 'blank') and hasattr(field, 'null') and 
                 field.blank and field.null and field.name != 'deleted_at'):
                
                field_value = getattr(instance, field.name, None)
                
                # Verificar si el campo está vacío
                if field_value is None or (isinstance(field_value, str) and field_value.strip() == ''):
                    missing_fields.append(field.name)
        
        total_fields = len([f for f in fields if hasattr(f, 'blank') and hasattr(f, 'null') 
                           and not f.blank and not f.null and not f.auto_created and not f.is_relation])
        filled_fields = total_fields - len(missing_fields)
        
        return {
            'color': 'warning' if len(missing_fields) > 0 else 'success',
            'is_complete': len(missing_fields) == 0,
            'missing_fields': missing_fields,
            'total_fields': total_fields,
            'filled_fields': filled_fields
        }
    
    @staticmethod
    def check_completeness_by_instance(instance: models.Model) -> Dict[str, Any]:
        """
        Verifica la completitud de una instancia específica del modelo.
        
        Args:
            instance: Instancia del modelo Django
            
        Returns:
            dict: Diccionario con información sobre la completitud del registro
        """
        missing_fields = []
        
        # Obtener todos los campos del modelo
        fields = instance._meta.get_fields()
        
        for field in fields:
            # Solo verificar campos que no son automáticos y no tienen blank=True y null=True
            if (hasattr(field, 'blank') and hasattr(field, 'null') and 
                 field.blank and field.null and field.name != 'deleted_at'):
                
                field_value = getattr(instance, field.name, None)
                
                # Verificar si el campo está vacío
                if field_value is None or (isinstance(field_value, str) and field_value.strip() == ''):
                    missing_fields.append(field.name)
        
        total_fields = len([f for f in fields if hasattr(f, 'blank') and hasattr(f, 'null') 
                           and not f.blank and not f.null and not f.auto_created and not f.is_relation])
        filled_fields = total_fields - len(missing_fields)
        
        return {
            'color': 'warning' if len(missing_fields) > 0 else 'success',
            'is_complete': len(missing_fields) == 0,
            'missing_fields': missing_fields,
            'total_fields': total_fields,
            'filled_fields': filled_fields
        }


def check_model_completeness(model_class: Type[models.Model], instance_id: int) -> Dict[str, Any]:
    """
    Función de conveniencia para verificar la completitud de un modelo.
    
    Args:
        model_class: Clase del modelo Django
        instance_id: ID del registro a verificar
        
    Returns:
        dict: Diccionario con información sobre la completitud del registro
    """
    return CompletenessChecker.check_completeness(model_class, instance_id)


def check_instance_completeness(instance: models.Model) -> Dict[str, Any]:
    """
    Función de conveniencia para verificar la completitud de una instancia.
    
    Args:
        instance: Instancia del modelo Django
        
    Returns:
        dict: Diccionario con información sobre la completitud del registro
    """
    return CompletenessChecker.check_completeness_by_instance(instance) 