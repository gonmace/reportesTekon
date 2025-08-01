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
from .models import AvanceProyecto, RegVisita
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
    """Vista para mostrar elementos específicos de registros de visita."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG
    
    def get(self, request, registro_id, paso_nombre):
        """Sobrescribir para manejar el paso avance_proyecto de manera especial."""
        if paso_nombre == 'avance_proyecto':
            return self.render_avance_proyecto_view(request, registro_id)
        return super().get(request, registro_id, paso_nombre)
    
    def render_avance_proyecto_view(self, request, registro_id):
        """Renderizar vista especial para avance_proyecto con tabla de avance físico."""
        from core.models.sites import Site
        from proyectos.models import EstructuraProyecto
        
        # Obtener el registro de visita
        registro = get_object_or_404(RegVisita, id=registro_id)
        sitio = registro.sitio
        
        # Obtener todas las estructuras de proyecto activas
        estructuras_proyecto = EstructuraProyecto.objects.filter(
            activo=True
        ).select_related(
            'grupo', 'componente'
        ).order_by('grupo__nombre', 'sort_order', 'orden')
        
        # Obtener avances específicos de este registro (por fecha)
        avances = AvanceProyecto.objects.filter(
            is_deleted=False,
            registro=registro  # Usar el registro específico en lugar del sitio
        ).select_related(
            'registro', 'proyecto', 'componente'
        ).order_by('created_at')
        
        # Filtrar por usuario si no es superusuario
        if not request.user.is_superuser:
            if registro.user != request.user:
                return JsonResponse({'error': 'No tiene permisos para este registro'}, status=403)
        
        # Crear diccionario de avances por estructura para este registro específico
        avances_por_estructura = {}
        for avance in avances:
            estructura = avance.proyecto
            if estructura:
                if estructura.id not in avances_por_estructura:
                    avances_por_estructura[estructura.id] = []
                avances_por_estructura[estructura.id].append(avance)
        
        # Preparar datos para la tabla
        tabla_estructura = []
        for estructura in estructuras_proyecto:
            # Obtener el avance para esta estructura en este registro específico
            avances_estructura = avances_por_estructura.get(estructura.id, [])
            # Ordenar por created_at para obtener el más reciente
            avances_estructura.sort(key=lambda x: x.created_at)
            ultimo_avance = avances_estructura[-1] if avances_estructura else None
            
            # Calcular totales
            ejecucion_anterior = 0
            ejecucion_actual = 0
            ejecucion_acumulada = 0
            ejecucion_total = 0
            
            if ultimo_avance:
                # Para el nuevo reporte, mostrar los valores correctos
                ejecucion_anterior = float(ultimo_avance.ejecucion_anterior)
                ejecucion_actual = float(ultimo_avance.ejecucion_actual)
                ejecucion_acumulada = float(ultimo_avance.ejecucion_acumulada)
                ejecucion_total = float(ultimo_avance.ejecucion_total)
            else:
                # Si no hay avance previo, calcular la ejecución total como 0
                ejecucion_total = 0
            
            tabla_estructura.append({
                'estructura': estructura,
                'componente': estructura.componente.nombre,
                'grupo': estructura.grupo.nombre,
                'incidencia': float(estructura.incidencia),
                'ejecucion_anterior': ejecucion_anterior,
                'ejecucion_actual': ejecucion_actual,
                'ejecucion_acumulada': ejecucion_acumulada,
                'ejecucion_total': ejecucion_total,
                'ultimo_avance': ultimo_avance,
                'tiene_avances': len(avances_estructura) > 0
            })
        
        # Calcular totales del proyecto
        total_incidencia = sum(item['incidencia'] for item in tabla_estructura)
        total_ejecucion = sum(item['ejecucion_total'] for item in tabla_estructura)
        porcentaje_avance_total = (total_ejecucion / total_incidencia * 100) if total_incidencia > 0 else 0
        
        context = {
            'registro': registro,
            'sitio': sitio,
            'tabla_estructura': tabla_estructura,
            'total_incidencia': total_incidencia,
            'total_ejecucion': total_ejecucion,
            'porcentaje_avance_total': porcentaje_avance_total,
            'title': f'Avance Físico del Proyecto - {sitio.name} - {registro.created_at.strftime("%d/%m/%Y")}',
            'description': f'Estructura del proyecto y avances físicos para el sitio {sitio.name} - Registro del {registro.created_at.strftime("%d/%m/%Y")}',
            'paso_nombre': 'avance_proyecto',
            'registro_id': registro_id,
            'fecha_registro': registro.created_at.strftime("%d/%m/%Y"),
        }
        
        return render(request, 'reg_visita/avance_proyecto_sitio.html', context)


class ActivarRegistroView(GenericActivarRegistroView):
    """Vista para activar registros de visita."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG


# ============================================================================
# VISTAS PARA TABLA EDITABLE
# ============================================================================

@method_decorator(csrf_exempt, name='dispatch')
class EstructurasProyectoAPIView(LoginRequiredMixin, View):
    """Vista API para obtener la lista de estructuras de proyecto disponibles."""
    
    def get(self, request):
        """Obtener lista de estructuras de proyecto activas."""
        try:
            from proyectos.models import EstructuraProyecto
            
            # Obtener estructuras de proyecto activas
            estructuras = EstructuraProyecto.objects.filter(activo=True).order_by('nombre')
            
            # Serializar datos
            data = []
            for estructura in estructuras:
                data.append({
                    'id': estructura.id,
                    'nombre': str(estructura),
                    'descripcion': estructura.descripcion or '',
                    'estado': estructura.estado
                })
            
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


@method_decorator(csrf_exempt, name='dispatch')
class ComponentesAPIView(LoginRequiredMixin, View):
    """Vista API para obtener la lista de componentes disponibles."""
    
    def get(self, request):
        """Obtener lista de componentes activos."""
        try:
            from proyectos.models import Componente
            
            # Obtener componentes activos
            componentes = Componente.objects.filter(activo=True).order_by('nombre')
            
            # Serializar datos
            data = []
            for componente in componentes:
                data.append({
                    'id': componente.id,
                    'nombre': str(componente),
                    'descripcion': componente.descripcion or '',
                    'estado': componente.estado
                })
            
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
            
            # Actualizar campos
            for field_name, value in data.items():
                if hasattr(instance, field_name):
                    setattr(instance, field_name, value)
            
            # Guardar instancia
            instance.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Campo actualizado correctamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def delete(self, request, pk):
        """Eliminar registro."""
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
            
            # Eliminar instancia (soft delete)
            instance.is_deleted = True
            instance.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Registro eliminado exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class AvanceProyectoTableAPIView(EditableTableAPIView):
    """Vista API para tabla editable de avances de proyecto."""
    
    def get_model_class(self):
        return AvanceProyecto
    
    def get_columns_config(self):
        from .config import avances_proyecto_columns
        return avances_proyecto_columns
    
    def get(self, request):
        """Obtener todos los registros de avances de proyecto con información de proyectos y componentes."""
        try:
            model_class = self.get_model_class()
            columns_config = self.get_columns_config()
            
            # Obtener datos del modelo con prefetch de proyecto y componente
            queryset = model_class.objects.filter(is_deleted=False).select_related('proyecto', 'componente')
            
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
                        
                        # Manejo especial para campos de relación
                        if field_name in ['proyecto', 'componente']:
                            if value:
                                row_data[field_name] = value.id
                                row_data[f'{field_name}_nombre'] = str(value)
                            else:
                                row_data[field_name] = None
                                row_data[f'{field_name}_nombre'] = ''
                        else:
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
        """Crear nuevo registro de avance de proyecto."""
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
                    value = data[field_name]
                    
                    # Manejo especial para campos de relación
                    if field_name == 'proyecto' and value:
                        from proyectos.models import EstructuraProyecto
                        try:
                            proyecto = EstructuraProyecto.objects.get(id=value)
                            setattr(instance, field_name, proyecto)
                        except EstructuraProyecto.DoesNotExist:
                            # Si el proyecto no existe, no asignar
                            pass
                    elif field_name == 'componente' and value:
                        from proyectos.models import Componente
                        try:
                            componente = Componente.objects.get(id=value)
                            setattr(instance, field_name, componente)
                        except Componente.DoesNotExist:
                            # Si el componente no existe, no asignar
                            pass
                    else:
                        setattr(instance, field_name, value)
            
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
    
    def patch(self, request, pk):
        """Actualizar campo específico de avance de proyecto."""
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
            
            # Actualizar campos
            for field_name, value in data.items():
                if hasattr(instance, field_name):
                    # Manejo especial para campos de relación
                    if field_name == 'proyecto':
                        if value:
                            from proyectos.models import EstructuraProyecto
                            try:
                                proyecto = EstructuraProyecto.objects.get(id=value)
                                setattr(instance, field_name, proyecto)
                            except EstructuraProyecto.DoesNotExist:
                                # Si el proyecto no existe, no asignar
                                pass
                        else:
                            setattr(instance, field_name, None)
                    elif field_name == 'componente':
                        if value:
                            from proyectos.models import Componente
                            try:
                                componente = Componente.objects.get(id=value)
                                setattr(instance, field_name, componente)
                            except Componente.DoesNotExist:
                                # Si el componente no existe, no asignar
                                pass
                        else:
                            setattr(instance, field_name, None)
                    else:
                        setattr(instance, field_name, value)
            
            # Guardar instancia
            instance.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Campo actualizado correctamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class EditableTableView(LoginRequiredMixin, View):
    """Vista base para tablas editables."""
    
    def get_table_config(self):
        """Obtiene la configuración de la tabla. Debe ser sobrescrito."""
        raise NotImplementedError("Debe implementar get_table_config()")
    
    def get(self, request):
        """Renderizar tabla editable."""
        self.table_config = self.get_table_config()
        
        context = {
            'title': self.table_config['title'],
            'description': self.table_config['description'],
            'columns': self.table_config['columns'],
            'api_url': self.table_config['api_url'],
            'allow_create': self.table_config['allow_create'],
            'allow_edit': self.table_config['allow_edit'],
            'allow_delete': self.table_config['allow_delete'],
            'page_length': self.table_config['page_length']
        }
        
        return render(request, 'components/editable_table.html', context)


class AvanceProyectoTableView(EditableTableView):
    """Vista para tabla editable de avances de proyecto."""
    
    def get_table_config(self):
        from .config import avances_proyecto_columns
        return {
            'title': 'Avances de Proyecto',
            'description': 'Administre los avances de ejecución de proyectos. Puede editar los porcentajes de ejecución y seleccionar la estructura de proyecto y componente relacionado directamente en la tabla.',
            'columns': avances_proyecto_columns,
            'model_class': AvanceProyecto,
            'api_url': '/reg_visita/api/avances_proyecto/',
            'allow_create': True,
            'allow_edit': True,
            'allow_delete': True,
            'page_length': 10
        }


@method_decorator(csrf_exempt, name='dispatch')
class AvanceFisicoInlineUpdateView(LoginRequiredMixin, View):
    """
    Vista para actualizar avances físicos inline desde reg_visita
    """
    
    def post(self, request, sitio_id):
        """Actualizar avances físicos de manera inline."""
        try:
            from core.models.sites import Site
            from proyectos.models import EstructuraProyecto
            from decimal import Decimal
            
            # Obtener sitio
            sitio = get_object_or_404(Site, id=sitio_id)
            
            # Obtener datos del request
            data = json.loads(request.body)
            updates = data.get('updates', [])
            registro_id = data.get('registro_id')  # Nuevo campo para el registro específico
            
            if not updates:
                return JsonResponse({'error': 'No se proporcionaron datos para actualizar'}, status=400)
            
            # Obtener el registro específico
            if registro_id:
                registro = get_object_or_404(RegVisita, id=registro_id, sitio=sitio)
            else:
                # Fallback: usar el registro más reciente del sitio
                registro = RegVisita.objects.filter(sitio=sitio).order_by('-created_at').first()
                if not registro:
                    return JsonResponse({'error': 'No se encontró registro para este sitio'}, status=400)
            
            # Verificar permisos
            if not request.user.is_superuser:
                if registro.user != request.user:
                    return JsonResponse({'error': 'No tiene permisos para este registro'}, status=403)
            
            # Procesar cada actualización
            for update in updates:
                estructura_id = update.get('estructura_id')
                ejecucion_anterior = Decimal(str(update.get('ejecucion_anterior', 0)))
                ejecucion_actual = Decimal(str(update.get('ejecucion_actual', 0)))
                
                if not estructura_id:
                    continue
                
                try:
                    estructura = EstructuraProyecto.objects.get(id=estructura_id)
                except EstructuraProyecto.DoesNotExist:
                    continue
                
                # Buscar o crear avance para esta estructura en este registro específico
                avance, created = AvanceProyecto.objects.get_or_create(
                    registro=registro,  # Usar el registro específico
                    proyecto=estructura,
                    defaults={
                        'componente': estructura.componente,
                        'ejecucion_anterior': ejecucion_anterior,
                        'ejecucion_actual': ejecucion_actual,
                        'ejecucion_acumulada': max(ejecucion_anterior, ejecucion_actual),
                        'ejecucion_total': (max(ejecucion_anterior, ejecucion_actual) * estructura.incidencia) / 100,
                        'comentarios': f'Avance actualizado desde reg_visita - {registro.created_at.strftime("%d/%m/%Y")}'
                    }
                )
                
                if not created:
                    # Actualizar avance existente
                    avance.ejecucion_anterior = ejecucion_anterior
                    avance.ejecucion_actual = ejecucion_actual
                    avance.ejecucion_acumulada = max(ejecucion_anterior, ejecucion_actual)
                    avance.ejecucion_total = (max(ejecucion_anterior, ejecucion_actual) * estructura.incidencia) / 100
                    avance.comentarios = f'Avance actualizado desde reg_visita - {registro.created_at.strftime("%d/%m/%Y")}'
                    avance.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Avances actualizados correctamente para el registro del {registro.created_at.strftime("%d/%m/%Y")}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AvanceFisicoNuevoReporteView(LoginRequiredMixin, View):
    """
    Vista para crear un nuevo reporte de avance físico desde reg_visita
    """
    
    def post(self, request, sitio_id):
        """Crear un nuevo reporte de avance físico."""
        try:
            from core.models.sites import Site
            from proyectos.models import EstructuraProyecto
            from decimal import Decimal
            
            # Obtener sitio
            sitio = get_object_or_404(Site, id=sitio_id)
            
            # Obtener datos del request
            data = json.loads(request.body)
            registro_id = data.get('registro_id')  # Nuevo campo para el registro específico
            
            # Obtener el registro específico
            if registro_id:
                registro = get_object_or_404(RegVisita, id=registro_id, sitio=sitio)
            else:
                # Fallback: usar el registro más reciente del sitio
                registro = RegVisita.objects.filter(sitio=sitio).order_by('-created_at').first()
                if not registro:
                    return JsonResponse({'error': 'No se encontró registro para este sitio'}, status=400)
            
            # Verificar permisos
            if not request.user.is_superuser:
                if registro.user != request.user:
                    return JsonResponse({'error': 'No tiene permisos para este registro'}, status=403)
            
            # Obtener todas las estructuras de proyecto activas
            estructuras = EstructuraProyecto.objects.filter(activo=True)
            
            # Crear avances para cada estructura en este registro específico
            avances_creados = 0
            for estructura in estructuras:
                # Verificar si ya existe un avance para esta estructura en este registro específico
                avance_existente = AvanceProyecto.objects.filter(
                    registro=registro,  # Usar el registro específico
                    proyecto=estructura,
                    is_deleted=False
                ).order_by('-created_at').first()
                
                if avance_existente:
                    # Usar los valores del último avance como ejecución anterior
                    ejecucion_anterior = avance_existente.ejecucion_acumulada
                    ejecucion_actual = Decimal('0.00')
                else:
                    # Si no hay avance previo, empezar desde 0
                    ejecucion_anterior = Decimal('0.00')
                    ejecucion_actual = Decimal('0.00')
                
                # Crear nuevo avance
                avance = AvanceProyecto.objects.create(
                    registro=registro,  # Usar el registro específico
                    proyecto=estructura,
                    componente=estructura.componente,
                    ejecucion_anterior=ejecucion_anterior,
                    ejecucion_actual=ejecucion_actual,
                    ejecucion_acumulada=max(ejecucion_anterior, ejecucion_actual),
                    ejecucion_total=(max(ejecucion_anterior, ejecucion_actual) * estructura.incidencia) / 100,
                    comentarios=f'Nuevo reporte de avance físico creado desde reg_visita - {registro.created_at.strftime("%d/%m/%Y")}'
                )
                avances_creados += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Se crearon {avances_creados} nuevos reportes de avance físico para el registro del {registro.created_at.strftime("%d/%m/%Y")}',
                'avances_creados': avances_creados
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)