"""
Vistas genéricas para manejar elementos usando las clases de componentes.
"""

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from registros_txtss.models import Registros
from registros.components.utils import handle_elemento_ajax_request


class ElementoView(LoginRequiredMixin, View):
    """
    Vista genérica para manejar elementos de registro.
    """
    
    def get(self, request, registro_id, tipo_elemento):
        """
        Maneja peticiones GET para mostrar el formulario del elemento.
        """
        try:
            # Obtener el registro
            registro = get_object_or_404(Registros, id=registro_id)
            
            # Obtener la clase del elemento basada en el tipo
            elemento_class = self.get_elemento_class(tipo_elemento)
            if not elemento_class:
                return JsonResponse({'error': f'Tipo de elemento no válido: {tipo_elemento}'}, status=400)
            
            # Crear instancia del elemento
            elemento = elemento_class(registro)
            
            # Obtener instancia existente
            instance = elemento.get_or_create()
            if instance:
                elemento = elemento_class(registro, instance)
            
            # Obtener formulario
            form = elemento.get_form()
            
            # Obtener sub-elementos
            sub_elementos = elemento.get_all_sub_elementos()
            
            # Preparar contexto
            context = {
                'elemento': elemento,
                'form': form,
                'instance': instance,
                'sub_elementos': sub_elementos,
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
            
            # Obtener la clase del elemento basada en el tipo
            elemento_class = self.get_elemento_class(tipo_elemento)
            if not elemento_class:
                return JsonResponse({'error': f'Tipo de elemento no válido: {tipo_elemento}'}, status=400)
            
            # Crear instancia del elemento
            elemento = elemento_class(registro)
            
            # Obtener instancia existente
            instance = elemento.get_or_create()
            if instance:
                elemento = elemento_class(registro, instance)
            
            # Manejar la petición usando la función genérica
            return handle_elemento_ajax_request(request, elemento)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def get_elemento_class(self, tipo_elemento):
        """
        Obtiene la clase del elemento basada en el tipo.
        """
        from registros_txtss.elementos import ElementoSitio, ElementoAcceso, ElementoEmpalme
        
        elementos_map = {
            'sitio': ElementoSitio,
            'acceso': ElementoAcceso,
            'empalme': ElementoEmpalme,
        }
        
        return elementos_map.get(tipo_elemento)
    
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