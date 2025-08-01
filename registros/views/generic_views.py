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
        self.template_name = self.registro_config.list_template
    
    def get_registro_config(self):
        """Obtiene la configuración del registro. Debe ser sobrescrito."""
        raise NotImplementedError("Debe implementar get_registro_config()")
    
    def get_form_class(self):
        """Retorna el formulario configurado para el modelo específico."""
        return create_activar_registro_form(
            registro_model=self.registro_config.registro_model,
            title_default=self.registro_config.title,
            description_default=f'Registro {self.registro_config.title} activado desde el formulario'
        )
    
    def form_valid(self, form):
        try:
            # Verificar si ya existe un registro para este sitio y usuario
            sitio = form.cleaned_data['sitio']
            user = form.cleaned_data['user']
            
            existing_registro = self.registro_config.registro_model.objects.filter(
                sitio=sitio, 
                user=user
            ).first()
            
            if existing_registro:
                if hasattr(existing_registro, 'is_deleted') and existing_registro.is_deleted:
                    # Si existe pero está marcado como eliminado, reactivarlo
                    existing_registro.is_deleted = False
                    existing_registro.save()
                    registro = existing_registro
                else:
                    # Si ya existe y está activo, mostrar error
                    error_message = f'Ya existe un registro activo para el sitio {sitio.name} y el usuario {user.username}'
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
                registro = form.save()
            
            messages.success(self.request, f'Registro activado exitosamente para {registro.sitio.name}')
            
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Registro activado exitosamente para {registro.sitio.name}'
                })
            else:
                return redirect(f'{self.registro_config.app_namespace}:list')
        except Exception as e:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
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
            'show_activate_button': True,
            'activate_button_text': 'Activar Registro',
            'activar_url': self.request.build_absolute_uri(f'/{self.registro_config.app_namespace}/activar/'),
            'modal_template': 'components/activar_registro_form.html',
        })
        if getattr(self.registro_config, 'header_title', None):
            context['header_title'] = self.registro_config.header_title
        return context 