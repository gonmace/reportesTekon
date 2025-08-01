from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from decimal import Decimal
from datetime import datetime
import json

from reg_visita.models import AvanceProyecto
from reg_visita.forms import AvanceProyectoForm
from proyectos.forms import AvanceFisicoForm
from proyectos.models import Componente, Grupo, EstructuraProyecto


class AvanceFisicoListView(LoginRequiredMixin, ListView):
    """
    Vista para listar todos los avances físicos de proyectos por sitio
    """
    model = AvanceProyecto
    template_name = 'proyectos/avance_fisico_list.html'
    context_object_name = 'avances'
    paginate_by = 20

    def get_queryset(self):
        queryset = AvanceProyecto.objects.filter(is_deleted=False).select_related(
            'registro__sitio', 'registro', 'proyecto', 'componente'
        ).order_by('registro__sitio__name', '-created_at')
        
        # Filtrar por usuario si no es superusuario
        if not self.request.user.is_superuser:
            queryset = queryset.filter(registro__user=self.request.user)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Avances Físicos de Proyectos por Sitio'
        context['description'] = 'Administre los avances de ejecución física organizados por sitio'
        
        # Agrupar avances por sitio
        avances_por_sitio = {}
        for avance in self.get_queryset():
            sitio = avance.registro.sitio if avance.registro else None
            if sitio:
                if sitio.id not in avances_por_sitio:
                    avances_por_sitio[sitio.id] = {
                        'sitio': sitio,
                        'avances': []
                    }
                avances_por_sitio[sitio.id]['avances'].append(avance)
        
        context['avances_por_sitio'] = avances_por_sitio
        return context


class AvanceFisicoCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear un nuevo avance físico
    """
    model = AvanceProyecto
    form_class = AvanceFisicoForm
    template_name = 'proyectos/avance_fisico_form.html'
    success_url = reverse_lazy('proyectos:avance_fisico_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        # Obtener parámetros de la URL
        sitio_id = self.request.GET.get('sitio')
        estructura_id = self.request.GET.get('estructura')
        
        if sitio_id:
            kwargs['sitio_id'] = sitio_id
        if estructura_id:
            kwargs['estructura_id'] = estructura_id
            
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Avance Físico'
        context['description'] = 'Complete los datos del nuevo avance físico'
        
        # Obtener parámetros de la URL
        sitio_id = self.request.GET.get('sitio')
        estructura_id = self.request.GET.get('estructura')
        
        if sitio_id:
            from core.models.sites import Site
            try:
                context['sitio_seleccionado'] = Site.objects.get(id=sitio_id)
            except Site.DoesNotExist:
                pass
                
        if estructura_id:
            try:
                context['estructura_seleccionada'] = EstructuraProyecto.objects.get(id=estructura_id)
            except EstructuraProyecto.DoesNotExist:
                pass
        
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Avance físico creado exitosamente.')
        return super().form_valid(form)


class AvanceFisicoUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vista para editar un avance físico existente
    """
    model = AvanceProyecto
    form_class = AvanceFisicoForm
    template_name = 'proyectos/avance_fisico_form.html'
    success_url = reverse_lazy('proyectos:avance_fisico_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Avance Físico'
        context['description'] = 'Modifique los datos del avance físico'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Avance físico actualizado exitosamente.')
        return super().form_valid(form)


class AvanceFisicoDeleteView(LoginRequiredMixin, DeleteView):
    """
    Vista para eliminar un avance físico
    """
    model = AvanceProyecto
    template_name = 'proyectos/avance_fisico_confirm_delete.html'
    success_url = reverse_lazy('proyectos:avance_fisico_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Avance físico eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class AvanceFisicoAPIView(LoginRequiredMixin, View):
    """
    Vista API para operaciones CRUD de avances físicos
    """
    
    def get(self, request):
        """Obtener todos los avances físicos"""
        try:
            queryset = AvanceProyecto.objects.filter(is_deleted=False).select_related(
                'registro', 'proyecto', 'componente'
            )
            
            # Filtrar por usuario si no es superusuario
            if not request.user.is_superuser:
                queryset = queryset.filter(registro__user=request.user)
            
            data = []
            for avance in queryset:
                data.append({
                    'id': avance.id,
                    'registro': avance.registro.title if avance.registro else '',
                    'proyecto': str(avance.proyecto) if avance.proyecto else '',
                    'componente': str(avance.componente) if avance.componente else '',
                    'comentarios': avance.comentarios or '',
                    'ejecucion_anterior': float(avance.ejecucion_anterior),
                    'ejecucion_actual': float(avance.ejecucion_actual),
                    'ejecucion_acumulada': float(avance.ejecucion_acumulada),
                    'ejecucion_total': float(avance.ejecucion_total),
                    'created_at': avance.created_at.strftime('%Y-%m-%d %H:%M'),
                    'updated_at': avance.updated_at.strftime('%Y-%m-%d %H:%M')
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

    def post(self, request):
        """Crear nuevo avance físico"""
        try:
            data = json.loads(request.body)
            form = AvanceProyectoForm(data)
            
            if form.is_valid():
                avance = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Avance físico creado exitosamente',
                    'id': avance.id
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def patch(self, request, pk):
        """Actualizar avance físico existente"""
        try:
            avance = get_object_or_404(AvanceProyecto, pk=pk)
            data = json.loads(request.body)
            
            # Verificar permisos
            if not request.user.is_superuser and avance.registro.user != request.user:
                return JsonResponse({'error': 'No tiene permisos para editar este registro'}, status=403)
            
            form = AvanceProyectoForm(data, instance=avance)
            
            if form.is_valid():
                form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Avance físico actualizado exitosamente'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def delete(self, request, pk):
        """Eliminar avance físico"""
        try:
            avance = get_object_or_404(AvanceProyecto, pk=pk)
            
            # Verificar permisos
            if not request.user.is_superuser and avance.registro.user != request.user:
                return JsonResponse({'error': 'No tiene permisos para eliminar este registro'}, status=403)
            
            avance.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Avance físico eliminado exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class ComponentesAPIView(LoginRequiredMixin, View):
    """
    Vista API para obtener componentes
    """
    
    def get(self, request):
        try:
            componentes = Componente.objects.filter(activo=True).order_by('nombre')
            data = [{'id': c.id, 'nombre': c.nombre} for c in componentes]
            
            return JsonResponse({
                'success': True,
                'data': data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class EstructurasProyectoAPIView(LoginRequiredMixin, View):
    """
    Vista API para obtener estructuras de proyecto
    """
    
    def get(self, request):
        try:
            estructuras = EstructuraProyecto.objects.filter(activo=True).select_related('grupo', 'componente').order_by('grupo__nombre', 'sort_order')
            data = []
            
            for estructura in estructuras:
                data.append({
                    'id': estructura.id,
                    'nombre': f"{estructura.grupo.nombre} - {estructura.componente.nombre} ({estructura.incidencia}%)",
                    'grupo': estructura.grupo.nombre,
                    'componente': estructura.componente.nombre,
                    'incidencia': float(estructura.incidencia)
                })
            
            return JsonResponse({
                'success': True,
                'data': data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class AvanceFisicoSitioView(LoginRequiredMixin, View):
    """
    Vista para mostrar el avance físico de un sitio específico
    """
    
    def get(self, request, sitio_id):
        from core.models.sites import Site
        
        sitio = get_object_or_404(Site, id=sitio_id)
        
        # Obtener todas las estructuras de proyecto activas (no solo las que tienen avances)
        estructuras_proyecto = EstructuraProyecto.objects.filter(
            activo=True
        ).select_related(
            'grupo', 'componente'
        ).order_by('grupo__nombre', 'sort_order', 'orden')
        
        # Obtener todos los avances del sitio
        avances = AvanceProyecto.objects.filter(
            is_deleted=False,
            registro__sitio=sitio
        ).select_related(
            'registro', 'proyecto', 'componente'
        ).order_by('created_at')
        
        # Filtrar por usuario si no es superusuario
        if not request.user.is_superuser:
            avances = avances.filter(registro__user=request.user)
        
        # Crear diccionario de avances por estructura
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
            # Obtener el último avance para esta estructura en este sitio
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
                # (incidencia * 0 / 100 = 0)
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
        # La ejecucion_total ya está ponderada por incidencia, por lo que la suma es correcta
        total_ejecucion = sum(item['ejecucion_total'] for item in tabla_estructura)
        # El porcentaje de avance total es la relación entre ejecución total e incidencia total
        porcentaje_avance_total = (total_ejecucion / total_incidencia * 100) if total_incidencia > 0 else 0
        
        context = {
            'sitio': sitio,
            'tabla_estructura': tabla_estructura,
            'total_incidencia': total_incidencia,
            'total_ejecucion': total_ejecucion,
            'porcentaje_avance_total': porcentaje_avance_total,
            'title': f'Avance Físico - {sitio.name}',
            'description': f'Estructura del proyecto y avances físicos para el sitio {sitio.name}',
        }
        
        return render(request, 'proyectos/avance_fisico_sitio.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class AvanceFisicoInlineUpdateView(LoginRequiredMixin, View):
    """
    Vista API para actualizar valores de ejecución de manera inline
    """
    
    def post(self, request, sitio_id):
        try:
            data = json.loads(request.body)
            estructura_id = data.get('estructura_id')
            campo = data.get('campo')  # 'ejecucion_anterior' o 'ejecucion_actual'
            valor = data.get('valor')
            
            if not all([estructura_id, campo, valor is not None]):
                return JsonResponse({
                    'success': False,
                    'error': 'Faltan parámetros requeridos'
                }, status=400)
            
            # Validar que el campo sea válido - permitir ejecucion_actual y ejecucion_anterior
            if campo not in ['ejecucion_actual', 'ejecucion_anterior']:
                return JsonResponse({
                    'success': False,
                    'error': 'Solo se puede editar la ejecución actual o anterior'
                }, status=400)
            
            # Validar que el valor sea un número
            try:
                valor = Decimal(str(valor))
                if valor < 0 or valor > 100:
                    return JsonResponse({
                        'success': False,
                        'error': 'El valor debe estar entre 0 y 100'
                    }, status=400)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': 'El valor debe ser un número válido'
                }, status=400)
            
            # Obtener el sitio
            from core.models.sites import Site
            sitio = get_object_or_404(Site, id=sitio_id)
            
            # Obtener la estructura
            estructura = get_object_or_404(EstructuraProyecto, id=estructura_id)
            
            # Obtener el último avance para esta estructura en este sitio
            ultimo_avance = AvanceProyecto.objects.filter(
                is_deleted=False,
                registro__sitio=sitio,
                proyecto=estructura
            ).order_by('-created_at').first()
            
            # Si no hay avance previo, crear uno nuevo
            if not ultimo_avance:
                # Crear un registro de visita si no existe
                from reg_visita.models import RegVisita
                registro_visita = RegVisita.objects.filter(
                    sitio=sitio,
                    user=request.user
                ).order_by('-created_at').first()
                
                if not registro_visita:
                    registro_visita = RegVisita.objects.create(
                        sitio=sitio,
                        user=request.user,
                        title=f"Avance automático - {sitio.name}"
                    )
                
                ultimo_avance = AvanceProyecto.objects.create(
                    registro=registro_visita,
                    proyecto=estructura,
                    componente=estructura.componente,
                    ejecucion_anterior=Decimal('0.00'),
                    ejecucion_actual=Decimal('0.00'),
                    ejecucion_acumulada=Decimal('0.00'),
                    ejecucion_total=Decimal('0.00')
                )
            
            # Actualizar el campo correspondiente
            if campo == 'ejecucion_actual':
                ultimo_avance.ejecucion_actual = valor
            elif campo == 'ejecucion_anterior':
                ultimo_avance.ejecucion_anterior = valor
            
            # El método save() del modelo recalculará automáticamente ejecucion_acumulada y ejecucion_total
            ultimo_avance.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Valor actualizado exitosamente',
                'data': {
                    'ejecucion_anterior': float(ultimo_avance.ejecucion_anterior),
                    'ejecucion_actual': float(ultimo_avance.ejecucion_actual),
                    'ejecucion_acumulada': float(ultimo_avance.ejecucion_acumulada),
                    'ejecucion_total': float(ultimo_avance.ejecucion_total)
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AvanceFisicoNuevoReporteView(LoginRequiredMixin, View):
    """
    Vista API para actualizar todos los avances existentes copiando valores de ejecución acumulada a anterior
    """
    
    def post(self, request, sitio_id):
        try:
            from core.models.sites import Site
            
            # Obtener el sitio
            sitio = get_object_or_404(Site, id=sitio_id)
            
            # Obtener todas las estructuras de proyecto activas
            estructuras_proyecto = EstructuraProyecto.objects.filter(activo=True)
            updated_count = 0
            
            for estructura in estructuras_proyecto:
                # Obtener el último avance para esta estructura en este sitio
                ultimo_avance = AvanceProyecto.objects.filter(
                    is_deleted=False,
                    registro__sitio=sitio,
                    proyecto=estructura
                ).order_by('-created_at').first()
                
                if ultimo_avance:
                    # Actualizar el avance existente
                    ultimo_avance.ejecucion_anterior = ultimo_avance.ejecucion_acumulada
                    ultimo_avance.ejecucion_actual = Decimal('0.00')
                    # El método save() del modelo recalculará automáticamente ejecucion_acumulada y ejecucion_total
                    ultimo_avance.save()
                    updated_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Reporte actualizado exitosamente. {updated_count} estructuras actualizadas.',
                'updated_count': updated_count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class DashboardProyectosView(LoginRequiredMixin, View):
    """
    Vista del dashboard de proyectos
    """
    
    def get(self, request):
        from core.models.sites import Site
        
        # Obtener sitios con avances
        sitios_con_avances = Site.objects.filter(
            regvisita__avanceproyecto__isnull=False
        ).distinct().order_by('name')
        
        # Filtrar por usuario si no es superusuario
        if not request.user.is_superuser:
            sitios_con_avances = sitios_con_avances.filter(
                regvisita__user=request.user
            ).distinct()
        
        context = {
            'title': 'Dashboard de Proyectos',
            'description': 'Panel de control para la gestión de proyectos y avances físicos',
            'total_avances': AvanceProyecto.objects.filter(is_deleted=False).count(),
            'total_componentes': Componente.objects.filter(activo=True).count(),
            'total_grupos': Grupo.objects.filter(activo=True).count(),
            'total_estructuras': EstructuraProyecto.objects.filter(activo=True).count(),
            'sitios_con_avances': sitios_con_avances,
        }
        
        return render(request, 'proyectos/dashboard.html', context)
