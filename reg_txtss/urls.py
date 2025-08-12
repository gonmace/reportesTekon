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
from .pdf_views import RegTxtssPDFView, preview_reg_txtss_individual

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
    
    # PDF
    path('pdf/<int:registro_id>/', RegTxtssPDFView.as_view(), name='pdf'),
    path('preview/<int:registro_id>/', preview_reg_txtss_individual, name='preview'),
    
    # URLs de photos específicas para reg_txtss
    path('<int:registro_id>/<str:step_name>/photos/', include('photos.urls')),
] 