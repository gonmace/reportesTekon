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
                    'message': f'Registro activado exitosamente para {registro.sitio.name} - {registro.fecha.strftime("%d/%m/%Y")}',
                    'redirect_url': f'/{self.registro_config.app_namespace}/{registro.id}/'
                })
            else:
                # Redirigir al nuevo registro creado para mostrar los steps
                return redirect(f'/{self.registro_config.app_namespace}/{registro.id}/')
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
            
            # Buscar el registro más reciente del mismo sitio y usuario
            # que tenga estructura asignada (sin importar la fecha)
            registro_anterior = self.registro_config.registro_model.objects.filter(
                sitio=sitio,
                user=user,
                is_active=True,
                is_deleted=False,
                estructura__isnull=False  # Solo registros con estructura
            ).exclude(
                id=nuevo_registro.id  # Excluir el registro actual
            ).order_by('-fecha').first()
            
            if not registro_anterior:
                print(f"No se encontró registro anterior con estructura para copiar datos")
                return
            
            print(f"Copiando datos del registro anterior: {registro_anterior.fecha}")
            print(f"Estructura anterior: {registro_anterior.estructura.nombre}")
            print(f"Estructura nueva: {nuevo_registro.estructura.nombre if nuevo_registro.estructura else 'N/A'}")
            
            # Si el nuevo registro no tiene estructura, copiar la del registro anterior
            if not nuevo_registro.estructura and registro_anterior.estructura:
                print(f"🔄 Copiando estructura del registro anterior: {registro_anterior.estructura.nombre}")
                nuevo_registro.estructura = registro_anterior.estructura
                nuevo_registro.save()
                print(f"✅ Estructura copiada exitosamente")
            
            # Verificar si las estructuras son compatibles
            if nuevo_registro.estructura and registro_anterior.estructura:
                if nuevo_registro.estructura.id != registro_anterior.estructura.id:
                    print(f"⚠️  Las estructuras son diferentes, copiando solo componentes comunes")
                    
                    # Obtener componentes comunes entre las estructuras
                    componentes_anterior = set(registro_anterior.estructura.componentes.values_list('componente_id', flat=True))
                    componentes_nueva = set(nuevo_registro.estructura.componentes.values_list('componente_id', flat=True))
                    componentes_comunes = componentes_anterior.intersection(componentes_nueva)
                    
                    print(f"Componentes comunes: {len(componentes_comunes)}")
                    
                    # Copiar solo avances de componentes comunes
                    avances_anteriores = AvanceComponente.objects.filter(
                        registro=registro_anterior,
                        componente_id__in=componentes_comunes
                    ).select_related('componente')
                else:
                    # Las estructuras son iguales, copiar todos los avances
                    avances_anteriores = AvanceComponente.objects.filter(
                        registro=registro_anterior
                    ).select_related('componente')
            else:
                # Si el nuevo registro no tiene estructura, no copiar nada
                print(f"⚠️  El nuevo registro no tiene estructura asignada")
                return
            
            # Crear avances para la nueva fecha copiando EJEC ACUMULADA a EJEC ANTERIOR
            for avance_anterior in avances_anteriores:
                # Copiar EJEC ACUMULADA de la fecha anterior a EJEC ANTERIOR de la nueva fecha
                # La nueva fecha inicia con ejec_actual=0 y ejec_acumulada=ejec_anterior
                print(f"DEBUG: Creando avance para {avance_anterior.componente.nombre}")
                print(f"DEBUG: - porcentaje_anterior: {avance_anterior.porcentaje_acumulado}")
                print(f"DEBUG: - porcentaje_actual: 0")
                print(f"DEBUG: - porcentaje_acumulado: {avance_anterior.porcentaje_acumulado}")
                
                nuevo_avance = AvanceComponente.objects.create(
                    registro=nuevo_registro,
                    componente=avance_anterior.componente,
                    fecha=date.today(),
                    porcentaje_anterior=avance_anterior.porcentaje_acumulado,  # Copiar acumulado anterior como anterior
                    porcentaje_actual=0,  # Ejecución actual en 0
                    porcentaje_acumulado=avance_anterior.porcentaje_acumulado,  # Mantener el mismo acumulado
                    comentarios=f"Copiado desde {registro_anterior.fecha.strftime('%d/%m/%Y')} - {avance_anterior.comentarios or 'Sin comentarios'}"
                )
                print(f"Creado avance para componente: {avance_anterior.componente.nombre}")
                print(f"  - Ejecución anterior: {avance_anterior.porcentaje_acumulado}% (copiada desde acumulada)")
                print(f"  - Ejecución actual: 0% (nueva fecha)")
                print(f"  - Ejecución acumulada: {avance_anterior.porcentaje_acumulado}% (mantenida)")
            
            print(f"Se copiaron {avances_anteriores.count()} avances del registro anterior")
            
        except Exception as e:
            print(f"Error al copiar datos de fecha anterior: {e}")
            # No interrumpir el flujo principal si hay error al copiar 