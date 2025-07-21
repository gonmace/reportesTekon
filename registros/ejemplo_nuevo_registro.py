"""
Ejemplo de cómo crear un nuevo registro usando el sistema simplificado.

Para crear un nuevo registro solo necesitas:
1. Definir los modelos (heredando de PasoBase)
2. Crear una configuración declarativa
3. Crear las vistas (heredando de las genéricas)
4. Configurar las URLs

¡Eso es todo! No necesitas crear formularios, elementos o vistas complejas.
"""

from django.db import models
from registros.models.base import RegistroBase
from registros.models.paso import PasoBase
from registros.components.registro_config import RegistroConfig, PasoConfig
from registros.views.generic_registro_views import (
    GenericRegistroListView, 
    GenericRegistroStepsView, 
    GenericElementoView
)


# 1. MODELOS (solo necesitas definir los campos específicos)
class RegistroEjemplo(RegistroBase):
    """Modelo para registros de ejemplo."""
    class Meta:
        verbose_name = "Registro Ejemplo"
        verbose_name_plural = "Registros Ejemplo"


class PasoUno(PasoBase):
    """Primer paso del registro ejemplo."""
    campo_uno = models.CharField(max_length=100, verbose_name='Campo Uno')
    campo_dos = models.TextField(blank=True, null=True, verbose_name='Campo Dos')
    
    class Meta:
        verbose_name = 'Paso Uno'
        verbose_name_plural = 'Pasos Uno'
    
    @staticmethod
    def get_etapa():
        return 'paso_uno'


class PasoDos(PasoBase):
    """Segundo paso del registro ejemplo."""
    campo_tres = models.CharField(max_length=100, verbose_name='Campo Tres')
    campo_cuatro = models.FloatField(verbose_name='Campo Cuatro')
    
    class Meta:
        verbose_name = 'Paso Dos'
        verbose_name_plural = 'Pasos Dos'
    
    @staticmethod
    def get_etapa():
        return 'paso_dos'


# 2. CONFIGURACIÓN DECLARATIVA
CONFIGURACION_EJEMPLO = RegistroConfig(
    registro_model=RegistroEjemplo,
    pasos={
        'paso_uno': PasoConfig(
            model=PasoUno,
            fields=['campo_uno', 'campo_dos'],
            title='Paso Uno',
            description='Descripción del primer paso.',
            success_message="Datos del paso uno guardados exitosamente.",
            error_message="Error al guardar los datos del paso uno.",
            css_classes={
                'campo_uno': 'input input-success sombra',
                'campo_dos': 'textarea textarea-warning sombra rows-2',
            }
        ),
        'paso_dos': PasoConfig(
            model=PasoDos,
            fields=['campo_tres', 'campo_cuatro'],
            title='Paso Dos',
            description='Descripción del segundo paso.',
            success_message="Datos del paso dos guardados exitosamente.",
            error_message="Error al guardar los datos del paso dos.",
            widgets={
                'campo_cuatro': 'NumberInput',
            },
            css_classes={
                'campo_tres': 'input input-success sombra',
                'campo_cuatro': 'input input-success sombra',
            }
        ),
    },
    title='Registros Ejemplo',
    breadcrumbs=[
        {'label': 'Inicio', 'url_name': 'dashboard:dashboard'},
        {'label': 'Ejemplo'}
    ]
)


# 3. VISTAS (solo necesitas heredar y retornar la configuración)
class ListRegistrosEjemploView(GenericRegistroListView):
    """Vista para listar registros ejemplo."""
    
    def get_registro_config(self):
        return CONFIGURACION_EJEMPLO


class StepsRegistroEjemploView(GenericRegistroStepsView):
    """Vista para mostrar los pasos de un registro ejemplo."""
    
    def get_registro_config(self):
        return CONFIGURACION_EJEMPLO


class ElementoRegistroEjemploView(GenericElementoView):
    """Vista para manejar elementos de registro ejemplo."""
    
    def get_registro_config(self):
        return CONFIGURACION_EJEMPLO


# 4. URLs (ejemplo de configuración)
"""
# En urls.py:
from django.urls import path
from .views import ListRegistrosEjemploView, StepsRegistroEjemploView, ElementoRegistroEjemploView

urlpatterns = [
    path('', ListRegistrosEjemploView.as_view(), name='list'),
    path('<int:registro_id>/', StepsRegistroEjemploView.as_view(), name='steps'),
    path('<int:registro_id>/<str:paso_nombre>/', ElementoRegistroEjemploView.as_view(), name='elemento'),
]
"""

# ¡Y eso es todo! El sistema genérico se encarga de:
# - Crear formularios automáticamente
# - Manejar la validación
# - Renderizar templates
# - Gestionar sub-elementos
# - Manejar AJAX
# - Y mucho más...

print("¡Crear un nuevo registro ahora es súper fácil!")
print("Solo necesitas:")
print("1. Modelos (campos específicos)")
print("2. Configuración declarativa")
print("3. Vistas (heredar de genéricas)")
print("4. URLs")
print("¡Y listo!") 