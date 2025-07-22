"""
URLs simplificadas para registros TX/TSS usando el sistema genérico.
"""

from django.urls import path, include
from .views import (
    ListRegistrosView,
    StepsRegistroView, 
    ElementoRegistroView,
    ActivarRegistroView
)

app_name = 'reg_txtss'

urlpatterns = [
    # Lista de registros
    path('', ListRegistrosView.as_view(), name='list'),
    
    # Activar registro
    path('activar/', ActivarRegistroView.as_view(), name='activar'),
    
    # Pasos del registro
    path('<int:registro_id>/', StepsRegistroView.as_view(), name='steps'),
    
    # Elementos específicos de cada paso
    path('<int:registro_id>/<str:paso_nombre>/', ElementoRegistroView.as_view(), name='elemento'),
    
    # Fotos - incluir las URLs de photos
    path('<int:registro_id>/<str:paso_nombre>/photos/', include('photos.urls_reg_txtss')),
] 