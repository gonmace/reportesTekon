"""
Vistas genéricas para manejar elementos usando configuración declarativa.
"""

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from registros_txtss.models import Registros
from registros.components.utils import handle_elemento_ajax_request
from registros.components.registro_config import ElementoGenerico
from registros_txtss.config import REGISTRO_CONFIG


class ElementoView(LoginRequiredMixin, View):
    """
    Vista genérica para manejar elementos de registro usando configuración declarativa.
    """
    
    def get(self, request, registro_id, tipo_elemento):
        """
        Maneja peticiones GET para mostrar el formulario del elemento.
        """
        try:
            # Obtener el registro
            registro = get_object_or_404(Registros, id=registro_id)
            
            # Obtener la configuración del elemento basada en el tipo
            elemento_config = self.get_elemento_config(tipo_elemento)
            if not elemento_config:
                return JsonResponse({'error': f'Tipo de elemento no válido: {tipo_elemento}'}, status=400)
            
            # Crear instancia del elemento
            elemento = ElementoGenerico(registro, elemento_config)
            
            # Obtener instancia existente
            instance = elemento.get_or_create()
            if instance:
                elemento = ElementoGenerico(registro, elemento_config, instance)
            
            # Obtener formulario
            form = elemento.get_form()
            
            # Preparar contexto
            context = {
                'elemento': elemento,
                'form': form,
                'instance': instance,
                'sub_elementos': elemento_config.sub_elementos,
                'registro': registro,
            }
            
            # Renderizar template
            return self.render_response(request, context)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def post(self, request, registro_id, tipo_elemento):
        """
        Maneja peticiones POST para guardar el elemento.
        """
        try:
            # Obtener el registro
            registro = get_object_or_404(Registros, id=registro_id)
            
            # Obtener la configuración del elemento basada en el tipo
            elemento_config = self.get_elemento_config(tipo_elemento)
            if not elemento_config:
                return JsonResponse({'error': f'Tipo de elemento no válido: {tipo_elemento}'}, status=400)
            
            # Crear instancia del elemento
            elemento = ElementoGenerico(registro, elemento_config)
            
            # Obtener instancia existente
            instance = elemento.get_or_create()
            if instance:
                elemento = ElementoGenerico(registro, elemento_config, instance)
            
            # Manejar la petición usando la función genérica
            return handle_elemento_ajax_request(request, elemento)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def get_elemento_config(self, tipo_elemento):
        """
        Obtiene la configuración del elemento basada en el tipo.
        """
        # Buscar en la configuración del registro
        if tipo_elemento in REGISTRO_CONFIG.pasos:
            return REGISTRO_CONFIG.pasos[tipo_elemento].elemento
        
        return None
    
    def render_response(self, request, context):
        """
        Renderiza la respuesta. Puede ser sobrescrito por subclases.
        """
        # Por defecto, devuelve JSON
        return JsonResponse({
            'success': True,
            'context': context
        })


class ElementoFormView(ElementoView):
    """
    Vista específica para renderizar formularios de elementos.
    """
    
    def render_response(self, request, context):
        """
        Renderiza el template del formulario.
        """
        from django.shortcuts import render
        
        template_name = context['elemento'].template_name or 'registros/templates/components/elemento_form.html'
        return render(request, template_name, context) 