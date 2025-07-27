"""
Vistas para registros reg_visita.
"""

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
import json

from registros.views.steps_views import (
    GenericRegistroStepsView,
    GenericElementoView,
    GenericRegistroTableListView
)
from registros.views.activation_views import GenericActivarRegistroView
from .models import RegVisita, Visita, Avance
from .config import REGISTRO_CONFIG


# ============================================================================
# VISTAS GENÉRICAS PARA REGISTROS
# ============================================================================

class ListRegistrosView(GenericRegistroTableListView):
    """Vista para listar registros de visita usando tabla genérica."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG


class StepsRegistroView(GenericRegistroStepsView):
    """Vista para mostrar los pasos de un registro de visita."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG


class ElementoRegistroView(GenericElementoView):
    """Vista para manejar elementos de registro de visita."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG


class ActivarRegistroView(GenericActivarRegistroView):
    """Vista para activar registros de visita."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG


# ============================================================================
# VISTAS PARA TABLA EDITABLE
# ============================================================================

@method_decorator(csrf_exempt, name='dispatch')
class EditableTableAPIView(LoginRequiredMixin, View):
    """
    Vista API para manejar operaciones CRUD de tablas editables.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_class = None
        self.columns_config = None
    
    def get_model_class(self):
        """Obtiene la clase del modelo. Debe ser sobrescrito."""
        raise NotImplementedError("Debe implementar get_model_class()")
    
    def get_columns_config(self):
        """Obtiene la configuración de columnas. Debe ser sobrescrito."""
        raise NotImplementedError("Debe implementar get_columns_config()")
    
    def get(self, request):
        """Obtener todos los registros."""
        try:
            model_class = self.get_model_class()
            columns_config = self.get_columns_config()
            
            # Obtener datos del modelo
            queryset = model_class.objects.filter(is_deleted=False)
            
            # Filtrar por usuario si no es superusuario
            if not request.user.is_superuser:
                if hasattr(model_class, 'user'):
                    queryset = queryset.filter(user=request.user)
                elif hasattr(model_class, 'registro'):
                    queryset = queryset.filter(registro__user=request.user)
            
            # Serializar datos
            data = []
            for obj in queryset:
                row_data = {}
                for column in columns_config:
                    field_name = column['key']
                    if hasattr(obj, field_name):
                        value = getattr(obj, field_name)
                        # Convertir fechas a string
                        if hasattr(value, 'strftime'):
                            value = value.strftime('%Y-%m-%d')
                        row_data[field_name] = value
                    else:
                        row_data[field_name] = None
                row_data['id'] = obj.id
                data.append(row_data)
            
            return JsonResponse({
                'success': True,
                'data': data,
                'total': len(data)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def post(self, request):
        """Crear nuevo registro."""
        try:
            model_class = self.get_model_class()
            columns_config = self.get_columns_config()
            
            # Obtener datos del request
            data = json.loads(request.body)
            
            # Crear instancia del modelo
            instance = model_class()
            
            # Asignar valores a los campos
            for column in columns_config:
                field_name = column['key']
                if field_name in data and hasattr(instance, field_name):
                    setattr(instance, field_name, data[field_name])
            
            # Asignar usuario si el modelo lo requiere
            if hasattr(instance, 'user'):
                instance.user = request.user
            
            # Guardar instancia
            instance.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Registro creado exitosamente',
                'id': instance.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def put(self, request, pk):
        """Actualizar registro completo."""
        try:
            model_class = self.get_model_class()
            columns_config = self.get_columns_config()
            
            # Obtener instancia
            instance = get_object_or_404(model_class, id=pk)
            
            # Verificar permisos
            if not request.user.is_superuser:
                if hasattr(instance, 'user') and instance.user != request.user:
                    return JsonResponse({'error': 'No tiene permisos para editar este registro'}, status=403)
                elif hasattr(instance, 'registro') and instance.registro.user != request.user:
                    return JsonResponse({'error': 'No tiene permisos para editar este registro'}, status=403)
            
            # Obtener datos del request
            data = json.loads(request.body)
            
            # Actualizar campos
            for column in columns_config:
                field_name = column['key']
                if field_name in data and hasattr(instance, field_name):
                    setattr(instance, field_name, data[field_name])
            
            # Guardar instancia
            instance.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Registro actualizado exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def patch(self, request, pk):
        """Actualizar campo específico."""
        try:
            model_class = self.get_model_class()
            
            # Obtener instancia
            instance = get_object_or_404(model_class, id=pk)
            
            # Verificar permisos
            if not request.user.is_superuser:
                if hasattr(instance, 'user') and instance.user != request.user:
                    return JsonResponse({'error': 'No tiene permisos para editar este registro'}, status=403)
                elif hasattr(instance, 'registro') and instance.registro.user != request.user:
                    return JsonResponse({'error': 'No tiene permisos para editar este registro'}, status=403)
            
            # Obtener datos del request
            data = json.loads(request.body)
            
            # Actualizar campo específico
            field_name = data.get('field')
            field_value = data.get('value')
            
            if field_name and hasattr(instance, field_name):
                setattr(instance, field_name, field_value)
                instance.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Campo actualizado exitosamente'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Campo no válido'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def delete(self, request, pk):
        """Eliminar registro (soft delete)."""
        try:
            model_class = self.get_model_class()
            
            # Obtener instancia
            instance = get_object_or_404(model_class, id=pk)
            
            # Verificar permisos
            if not request.user.is_superuser:
                if hasattr(instance, 'user') and instance.user != request.user:
                    return JsonResponse({'error': 'No tiene permisos para eliminar este registro'}, status=403)
                elif hasattr(instance, 'registro') and instance.registro.user != request.user:
                    return JsonResponse({'error': 'No tiene permisos para eliminar este registro'}, status=403)
            
            # Soft delete
            if hasattr(instance, 'is_deleted'):
                instance.is_deleted = True
                instance.save()
            else:
                instance.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Registro eliminado exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class VisitaTableAPIView(EditableTableAPIView):
    """Vista API para tabla editable de visitas."""
    
    def get_model_class(self):
        return Visita
    
    def get_columns_config(self):
        from .config import visitas_columns
        return visitas_columns


class AvanceTableAPIView(EditableTableAPIView):
    """Vista API para tabla editable de avances."""
    
    def get_model_class(self):
        return Avance
    
    def get_columns_config(self):
        from .config import avances_columns
        return avances_columns


class EditableTableView(LoginRequiredMixin, View):
    """Vista base para renderizar tablas editables."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_config = self.get_table_config()
    
    def get_table_config(self):
        """Obtiene la configuración de la tabla. Debe ser sobrescrito."""
        raise NotImplementedError("Debe implementar get_table_config()")
    
    def get(self, request):
        """Renderiza la tabla editable."""
        context = {
            'table_config': self.table_config,
            'columns': self.table_config['columns'],
            'title': self.table_config['title'],
            'description': self.table_config['description'],
            'api_url': self.table_config['api_url'],
            'allow_create': self.table_config['allow_create'],
            'allow_edit': self.table_config['allow_edit'],
            'allow_delete': self.table_config['allow_delete'],
            'page_length': self.table_config['page_length']
        }
        
        return render(request, 'components/editable_table.html', context)


class VisitaTableView(EditableTableView):
    """Vista para tabla editable de visitas."""
    
    def get_table_config(self):
        from .config import visitas_columns
        return {
            'title': 'Visitas',
            'description': 'Administre las visitas realizadas. Puede editar los comentarios directamente en la tabla.',
            'columns': visitas_columns,
            'model_class': Visita,
            'api_url': '/reg_visita/api/visitas/',
            'allow_create': True,
            'allow_edit': True,
            'allow_delete': True,
            'page_length': 10
        }


class AvanceTableView(EditableTableView):
    """Vista para tabla editable de avances."""
    
    def get_table_config(self):
        from .config import avances_columns
        return {
            'title': 'Avances',
            'description': 'Administre los avances del proyecto. Puede editar los detalles directamente en la tabla.',
            'columns': avances_columns,
            'model_class': Avance,
            'api_url': '/reg_visita/api/avances/',
            'allow_create': True,
            'allow_edit': True,
            'allow_delete': True,
            'page_length': 10
        }