"""
Ejemplo práctico: Cómo agregar un nuevo paso a la vista de pasos existente.

Este archivo muestra cómo extender la funcionalidad de StepsRegistroView
para incluir un nuevo paso llamado 'empalme'.
"""

from registrostxtss.views import StepsRegistroView

class StepsRegistroViewExtended(StepsRegistroView):
    """
    Vista extendida que incluye un paso adicional 'empalme'.
    
    Este ejemplo muestra cómo agregar un nuevo paso sin modificar
    la vista original, manteniendo la compatibilidad hacia atrás.
    """
    
    def get_steps_config(self):
        """
        Configuración extendida que incluye el paso 'empalme'.
        
        Returns:
            dict: Configuración de los pasos incluyendo el nuevo paso
        """
        # Obtener la configuración base
        config = super().get_steps_config()
        
        # Agregar el nuevo paso
        # Nota: Importar aquí para evitar dependencias circulares
        try:
            from registrostxtss.r_empalme.models import REmpalme
            config['empalme'] = {
                'model_class': REmpalme,
                'has_photos': True,
                'min_photo_count': 3  # Empalme requiere menos fotos
            }
        except ImportError:
            # Si el modelo no existe aún, no agregar el paso
            pass
        
        return config


# Ejemplo de cómo crear una vista completamente nueva
class MiNuevaVistaPasos(StepsRegistroView):
    """
    Ejemplo de una vista completamente nueva con pasos personalizados.
    """
    
    template_name = 'pages/mi_nueva_vista.html'
    
    def get_breadcrumbs(self):
        """Breadcrumbs personalizados para esta vista"""
        breadcrumbs = [
            {'label': 'Inicio', 'url_name': 'dashboard:dashboard'},
            {'label': 'Mi Nueva Sección', 'url_name': 'mi_seccion:list'}
        ]
        
        # Agregar breadcrumb del sitio
        registro_id = self.kwargs.get('registro_id')
        if registro_id:
            from django.shortcuts import get_object_or_404
            from registrostxtss.models.main_registrostxtss import RegistrosTxTss
            
            registro_txtss = get_object_or_404(RegistrosTxTss, id=registro_id)
            sitio_cod = registro_txtss.sitio.pti_cell_id or registro_txtss.sitio.operator_id
            breadcrumbs.append({'label': sitio_cod})
        
        return self._resolve_breadcrumbs(breadcrumbs)
    
    def get_steps_config(self):
        """
        Configuración personalizada para esta vista.
        
        Returns:
            dict: Configuración de los pasos específicos para esta vista
        """
        # Importar modelos específicos para esta vista
        from registrostxtss.r_mi_modelo.models import RMiModelo
        from registrostxtss.r_otro_modelo.models import ROtroModelo
        
        return {
            'inspeccion': {
                'model_class': RMiModelo,
                'has_photos': True,
                'min_photo_count': 5  # Inspección requiere más fotos
            },
            'documentacion': {
                'model_class': ROtroModelo,
                'has_photos': False  # Documentación no requiere fotos
            }
        }


# Ejemplo de cómo personalizar el contexto de un paso específico
class VistaConContextoPersonalizado(StepsRegistroView):
    """
    Ejemplo que muestra cómo personalizar el contexto de pasos específicos.
    """
    
    def generate_step_context(self, registro_txtss, model_class, has_photos, min_photo_count=4):
        """
        Genera contexto personalizado para cada paso.
        
        Args:
            registro_txtss: Instancia del registro principal
            model_class: Clase del modelo del paso
            has_photos: Si el paso tiene fotos
            min_photo_count: Número mínimo de fotos requeridas
            
        Returns:
            dict: Contexto del paso con información adicional
        """
        # Obtener el contexto base
        context = super().generate_step_context(registro_txtss, model_class, has_photos, min_photo_count)
        
        # Agregar información personalizada según el tipo de modelo
        etapa = model_class.get_etapa()
        
        if etapa == 'sitio':
            # Información adicional específica para sitio
            context['info_adicional'] = {
                'tipo': 'Inspección de sitio',
                'prioridad': 'Alta',
                'tiempo_estimado': '2 horas'
            }
        elif etapa == 'acceso':
            # Información adicional específica para acceso
            context['info_adicional'] = {
                'tipo': 'Evaluación de acceso',
                'prioridad': 'Media',
                'tiempo_estimado': '1 hora'
            }
        
        # Agregar información de progreso
        context['progreso'] = self.calcular_progreso(registro_txtss)
        
        return context
    
    def calcular_progreso(self, registro_txtss):
        """
        Calcula el progreso general del registro.
        
        Args:
            registro_txtss: Instancia del registro principal
            
        Returns:
            dict: Información de progreso
        """
        # Obtener todos los pasos configurados
        steps_config = self.get_steps_config()
        total_pasos = len(steps_config)
        pasos_completados = 0
        
        for step_name, config in steps_config.items():
            model_class = config['model_class']
            try:
                instance = model_class.objects.get(registro=registro_txtss)
                completeness_info = model_class.check_completeness(instance.id)
                if completeness_info['is_complete']:
                    pasos_completados += 1
            except model_class.DoesNotExist:
                pass
        
        porcentaje = (pasos_completados / total_pasos) * 100 if total_pasos > 0 else 0
        
        return {
            'total_pasos': total_pasos,
            'pasos_completados': pasos_completados,
            'porcentaje': round(porcentaje, 1),
            'color': 'success' if porcentaje == 100 else 'warning' if porcentaje > 50 else 'error'
        }


# Ejemplo de uso en URLs
"""
# registrostxtss/urls.py

from django.urls import path
from .views import StepsRegistroView
from .views.example_new_step import (
    StepsRegistroViewExtended, 
    MiNuevaVistaPasos, 
    VistaConContextoPersonalizado
)

urlpatterns = [
    # Vista original (sin cambios)
    path('steps/<int:registro_id>/', StepsRegistroView.as_view(), name='steps'),
    
    # Vista extendida con paso adicional
    path('steps-extended/<int:registro_id>/', StepsRegistroViewExtended.as_view(), name='steps_extended'),
    
    # Vista completamente nueva
    path('mi-vista/<int:registro_id>/', MiNuevaVistaPasos.as_view(), name='mi_vista'),
    
    # Vista con contexto personalizado
    path('steps-personalizado/<int:registro_id>/', VistaConContextoPersonalizado.as_view(), name='steps_personalizado'),
]
"""


# Ejemplo de template para la vista extendida
"""
<!-- templates/pages/steps_extended.html -->
{% extends "base.html" %}
{% load static %} 

{% block pre_content %}
    {% include 'components/common/breadcrumbs.html' %}
{% endblock pre_content %}

{% block content %}
<ul class="timeline timeline-vertical">
    <!-- Paso Sitio -->
    {% include 'components/step&photo.html' with 
        registro_id=sitio.registro_id 
        title="sitio" 
        photo_count=sitio.photo.count 
        color_form=sitio.completeness_info.color  
        color_photo=sitio.photo.color 
        first=True %}
        
    <!-- Paso Acceso -->
    {% include 'components/step.html' with 
        registro_id=acceso.registro_id 
        title="acceso" 
        color_form=acceso.completeness_info.color %}

    <!-- Nuevo Paso Empalme -->
    {% include 'components/step&photo.html' with 
        registro_id=empalme.registro_id 
        title="empalme" 
        photo_count=empalme.photo.count 
        color_form=empalme.completeness_info.color  
        color_photo=empalme.photo.color 
        last=True %}
</ul>
{% endblock %}
"""


# Ejemplo de template para vista con contexto personalizado
"""
<!-- templates/pages/steps_personalizado.html -->
{% extends "base.html" %}
{% load static %} 

{% block pre_content %}
    {% include 'components/common/breadcrumbs.html' %}
{% endblock pre_content %}

{% block content %}
<!-- Barra de progreso -->
<div class="mb-6">
    <div class="flex justify-between items-center mb-2">
        <span class="text-sm font-medium">Progreso General</span>
        <span class="text-sm text-gray-600">{{ progreso.pasos_completados }}/{{ progreso.total_pasos }}</span>
    </div>
    <div class="w-full bg-gray-200 rounded-full h-2">
        <div class="bg-{{ progreso.color }} h-2 rounded-full" 
             style="width: {{ progreso.porcentaje }}%"></div>
    </div>
    <div class="text-center mt-1">
        <span class="text-sm text-gray-600">{{ progreso.porcentaje }}% completado</span>
    </div>
</div>

<ul class="timeline timeline-vertical">
    {% for step_name, step_data in steps_config.items %}
        {% if step_data.has_photos %}
            {% include 'components/step&photo.html' with 
                registro_id=step_data.registro_id 
                title=step_name 
                photo_count=step_data.photo.count 
                color_form=step_data.completeness_info.color  
                color_photo=step_data.photo.color 
                first=forloop.first 
                last=forloop.last %}
        {% else %}
            {% include 'components/step.html' with 
                registro_id=step_data.registro_id 
                title=step_name 
                color_form=step_data.completeness_info.color 
                first=forloop.first 
                last=forloop.last %}
        {% endif %}
    {% endfor %}
</ul>

<!-- Información adicional de cada paso -->
<div class="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {% for step_name, step_data in steps_config.items %}
        {% if step_data.info_adicional %}
        <div class="card bg-base-100 shadow-sm">
            <div class="card-body">
                <h3 class="card-title text-lg">{{ step_name|title }}</h3>
                <div class="space-y-2">
                    <p><strong>Tipo:</strong> {{ step_data.info_adicional.tipo }}</p>
                    <p><strong>Prioridad:</strong> 
                        <span class="badge badge-{{ step_data.info_adicional.prioridad|lower }}">
                            {{ step_data.info_adicional.prioridad }}
                        </span>
                    </p>
                    <p><strong>Tiempo estimado:</strong> {{ step_data.info_adicional.tiempo_estimado }}</p>
                </div>
            </div>
        </div>
        {% endif %}
    {% endfor %}
</div>
{% endblock %}
""" 