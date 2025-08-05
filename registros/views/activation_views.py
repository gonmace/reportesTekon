"""
Vistas genéricas para registros.
"""

from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from registros.forms.activar import create_activar_registro_form
from typing import Dict, Any


class GenericActivarRegistroView(LoginRequiredMixin, FormView):
    """
    Vista genérica para activar registros.
    Puede ser usada por cualquier aplicación que herede de RegistroBase.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registro_config = self.get_registro_config()
        self.template_name = 'pages/activar_registro.html'
    
    def get_registro_config(self):
        """Obtiene la configuración del registro. Debe ser sobrescrito."""
        raise NotImplementedError("Debe implementar get_registro_config()")
    
    def get_form_class(self):
        """Retorna el formulario configurado para el modelo específico."""
        allow_multiple = getattr(self.registro_config, 'allow_multiple_per_site', False)
        project = getattr(self.registro_config, 'project', False)
        return create_activar_registro_form(
            registro_model=self.registro_config.registro_model,
            title_default=self.registro_config.title,
            description_default=f'Registro {self.registro_config.title} activado desde el formulario',
            allow_multiple_per_site=allow_multiple,
            project=project
        )
    
    def form_valid(self, form):
        try:
            # Debug: imprimir los datos del formulario
            print(f"Datos del formulario: {form.cleaned_data}")
            
            # Verificar si ya existe un registro para este sitio, usuario y fecha
            sitio = form.cleaned_data['sitio']
            user = form.cleaned_data['user']
            fecha = form.cleaned_data['fecha']
            
            # Validar que la fecha no esté vacía
            if not fecha:
                from datetime import date
                fecha = date.today()
                print(f"Fecha vacía, usando fecha actual: {fecha}")
            
            # Si no hay campo fecha en el formulario, usar fecha actual
            if 'fecha' not in form.cleaned_data:
                from datetime import date
                fecha = date.today()
                print(f"No hay campo fecha en formulario, usando fecha actual: {fecha}")
            
            print(f"Sitio: {sitio}, User: {user}, Fecha: {fecha}")
            
            existing_registro = self.registro_config.registro_model.objects.filter(
                sitio=sitio, 
                user=user,
                fecha=fecha
            ).first()
            
            if existing_registro:
                if hasattr(existing_registro, 'is_deleted') and existing_registro.is_deleted:
                    # Si existe pero está marcado como eliminado, reactivarlo
                    existing_registro.is_deleted = False
                    existing_registro.save()
                    registro = existing_registro
                else:
                    # Si ya existe y está activo, mostrar error
                    error_message = f'Ya existe un registro activo para el sitio {sitio.name}, usuario {user.username} y fecha {fecha.strftime("%d/%m/%Y")}'
                    if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'message': error_message
                        }, status=400)
                    else:
                        messages.error(self.request, error_message)
                        return self.form_invalid(form)
            else:
                # Crear nuevo registro
                try:
                    # Obtener el grupo de actividades seleccionado
                    grupo_actividades = form.cleaned_data.get('grupo_actividades')
                    
                    # Crear el registro usando el modelo dinámico
                    registro_data = {
                        'sitio': sitio,
                        'user': user,
                        'title': form.cleaned_data.get('title', ''),
                        'description': form.cleaned_data.get('description', ''),
                        'fecha': fecha,
                        'is_active': True,
                        'is_deleted': False
                    }
                    
                    # Agregar grupo_actividades si el modelo lo soporta
                    if hasattr(self.registro_config.registro_model, 'grupo_actividades'):
                        registro_data['grupo_actividades'] = grupo_actividades
                    
                    # Agregar estructura si el modelo lo soporta
                    estructura = form.cleaned_data.get('estructura')
                    if hasattr(self.registro_config.registro_model, 'estructura'):
                        registro_data['estructura'] = estructura
                    
                    registro = self.registro_config.registro_model.objects.create(**registro_data)
                    print(f"Registro creado exitosamente: {registro}")
                    
                    # Copiar datos de la fecha anterior si es una nueva fecha
                    self._copiar_datos_fecha_anterior(registro, sitio, user)
                    
                except Exception as save_error:
                    print(f"Error al guardar: {save_error}")
                    raise save_error
            
            messages.success(self.request, f'Registro activado exitosamente para {registro.sitio.name} - {registro.fecha.strftime("%d/%m/%Y")}')
            
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Registro activado exitosamente para {registro.sitio.name} - {registro.fecha.strftime("%d/%m/%Y")}'
                })
            else:
                return redirect(f'{self.registro_config.app_namespace}:list')
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error completo: {error_details}")
            
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error al activar registro: {str(e)}',
                    'details': error_details
                }, status=400)
            else:
                messages.error(self.request, f'Error al activar registro: {str(e)}')
                return self.form_invalid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Error en el formulario',
                'errors': form.errors
            }, status=400)
        else:
            return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': self.registro_config.title,
            'app_namespace': self.registro_config.app_namespace,
            'activar_url': self.request.build_absolute_uri(f'/{self.registro_config.app_namespace}/activar/'),
            'allow_multiple_per_site': getattr(self.registro_config, 'allow_multiple_per_site', False),
            'project': getattr(self.registro_config, 'project', False),
        })
        if getattr(self.registro_config, 'header_title', None):
            context['header_title'] = self.registro_config.header_title
        return context
    
    def _copiar_datos_fecha_anterior(self, nuevo_registro, sitio, user):
        """
        Copia los datos de la fecha anterior más reciente al nuevo registro.
        """
        try:
            from datetime import date
            from reg_construccion.models import AvanceComponente
            
            # Buscar el registro anterior más reciente del mismo sitio y usuario
            registro_anterior = self.registro_config.registro_model.objects.filter(
                sitio=sitio,
                user=user,
                fecha__lt=nuevo_registro.fecha,  # Fecha anterior a la nueva
                is_active=True,
                is_deleted=False
            ).order_by('-fecha').first()
            
            if not registro_anterior:
                print(f"No se encontró registro anterior para copiar datos")
                return
            
            print(f"Copiando datos del registro anterior: {registro_anterior.fecha}")
            
            # Copiar AvanceComponente del registro anterior
            avances_anteriores = AvanceComponente.objects.filter(
                registro=registro_anterior
            ).select_related('componente')
            
            for avance_anterior in avances_anteriores:
                # Crear nuevo avance con la fecha actual
                nuevo_avance = AvanceComponente.objects.create(
                    registro=nuevo_registro,
                    componente=avance_anterior.componente,
                    fecha=date.today(),
                    porcentaje_actual=avance_anterior.porcentaje_actual,
                    porcentaje_acumulado=avance_anterior.porcentaje_acumulado,
                    comentarios=f"Copiado desde {registro_anterior.fecha.strftime('%d/%m/%Y')} - {avance_anterior.comentarios or 'Sin comentarios'}"
                )
                print(f"Copiado avance para componente: {avance_anterior.componente.nombre}")
            
            print(f"Se copiaron {avances_anteriores.count()} avances del registro anterior")
            
        except Exception as e:
            print(f"Error al copiar datos de fecha anterior: {e}")
            # No interrumpir el flujo principal si hay error al copiar 