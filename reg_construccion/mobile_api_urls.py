"""
URLs específicas para las APIs móviles de reg_construccion.
"""

from django.urls import path
from .mobile_api_views import (
    sitios_activos_por_usuario,
    crear_nueva_fecha,
    llenar_objetivo,
    llenar_avance,
    llenar_tabla,
    subir_imagenes,
    obtener_registro_completo
)

app_name = 'mobile_api'

urlpatterns = [
    # 1. API para listar sitios activos por usuario
    path('sitios-activos/', sitios_activos_por_usuario, name='sitios_activos'),
    
    # 2. API para crear nueva fecha
    path('crear-fecha/', crear_nueva_fecha, name='crear_fecha'),
    
    # 3. API para llenar objetivo
    path('llenar-objetivo/', llenar_objetivo, name='llenar_objetivo'),
    
    # 4. API para llenar avance
    path('llenar-avance/', llenar_avance, name='llenar_avance'),
    
    # 5. API para llenar tabla
    path('llenar-tabla/', llenar_tabla, name='llenar_tabla'),
    
    # 6. API para subir imágenes
    path('subir-imagenes/', subir_imagenes, name='subir_imagenes'),
    
    # API adicional para obtener registro completo
    path('registro-completo/<int:registro_id>/', obtener_registro_completo, name='registro_completo'),
]
