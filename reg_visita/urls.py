"""
URLs para reg_visita.
"""

from django.urls import path
from . import views

app_name = 'reg_visita'

urlpatterns = [
    # URLs genéricas para registros
    path('', views.ListRegistrosView.as_view(), name='list'),
    path('activar/', views.ActivarRegistroView.as_view(), name='activar'),
    path('<int:registro_id>/', views.StepsRegistroView.as_view(), name='steps'),
    path('<int:registro_id>/steps/', views.StepsRegistroView.as_view(), name='steps_alt'),
    path('<int:registro_id>/<str:paso_nombre>/', views.ElementoRegistroView.as_view(), name='elemento'),
    
    # URLs para tablas editables
    path('api/avances_proyecto/', views.AvanceProyectoTableAPIView.as_view(), name='avances_proyecto_api'),
    path('api/avances_proyecto/<int:pk>/', views.AvanceProyectoTableAPIView.as_view(), name='avances_proyecto_api_detail'),
    path('api/estructuras_proyecto/', views.EstructurasProyectoAPIView.as_view(), name='estructuras_proyecto_api'),
    path('api/componentes/', views.ComponentesAPIView.as_view(), name='componentes_api'),
    
    # URLs para vistas de tabla editable
    path('avances_proyecto/', views.AvanceProyectoTableView.as_view(), name='avances_proyecto'),
    
    # URLs para manejo de avance físico desde reg_visita
    path('api/avance-fisico-inline-update/<int:sitio_id>/', views.AvanceFisicoInlineUpdateView.as_view(), name='avance_fisico_inline_update'),
    path('api/avance-fisico-nuevo-reporte/<int:sitio_id>/', views.AvanceFisicoNuevoReporteView.as_view(), name='avance_fisico_nuevo_reporte'),
]