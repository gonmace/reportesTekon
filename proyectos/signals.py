"""
Signals para manejar la eliminación segura de componentes.
"""

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Componente
from reg_visita.models import AvanceProyecto


@receiver(pre_delete, sender=Componente)
def handle_componente_pre_delete(sender, instance, **kwargs):
    """
    Signal que se ejecuta antes de eliminar un componente.
    Elimina todos los registros relacionados de manera segura.
    """
    try:
        # Eliminar avances de proyecto relacionados
        avances = AvanceProyecto.objects.filter(componente=instance)
        avances_count = avances.count()
        avances.delete()
        
        # Las estructuras de proyecto se eliminarán automáticamente por CASCADE
        
        print(f"Eliminados {avances_count} avances relacionados con el componente '{instance.nombre}'")
        
    except Exception as e:
        print(f"Error al eliminar registros relacionados con el componente '{instance.nombre}': {str(e)}")
        # No levantar la excepción aquí para evitar que se detenga la eliminación
        pass 