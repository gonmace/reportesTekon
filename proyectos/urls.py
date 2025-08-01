"""
URLs para la app proyectos.
"""

from django.urls import path
from . import views

app_name = 'proyectos'

urlpatterns = [
    # Dashboard principal de proyectos
    path('', views.DashboardProyectosView.as_view(), name='dashboard'),
    
    # URLs para avances físicos
    path('avances-fisicos/', views.AvanceFisicoListView.as_view(), name='avance_fisico_list'),
    path('avances-fisicos/crear/', views.AvanceFisicoCreateView.as_view(), name='avance_fisico_create'),
    path('avances-fisicos/<int:pk>/editar/', views.AvanceFisicoUpdateView.as_view(), name='avance_fisico_update'),
    path('avances-fisicos/<int:pk>/eliminar/', views.AvanceFisicoDeleteView.as_view(), name='avance_fisico_delete'),
    
    # URLs para avances físicos por sitio
    path('sitio/<int:sitio_id>/avance-fisico/', views.AvanceFisicoSitioView.as_view(), name='avance_fisico_sitio'),
    
    # URLs API para avances físicos
    path('api/avances-fisicos/', views.AvanceFisicoAPIView.as_view(), name='avance_fisico_api'),
    path('api/avances-fisicos/<int:pk>/', views.AvanceFisicoAPIView.as_view(), name='avance_fisico_api_detail'),
    
    # URL API para actualización inline de avances físicos
    path('sitio/<int:sitio_id>/avance-fisico/actualizar/', views.AvanceFisicoInlineUpdateView.as_view(), name='avance_fisico_inline_update'),
    
    # URL API para nuevo reporte
    path('sitio/<int:sitio_id>/avance-fisico/nuevo-reporte/', views.AvanceFisicoNuevoReporteView.as_view(), name='avance_fisico_nuevo_reporte'),
    
    # URLs API para datos de soporte
    path('api/componentes/', views.ComponentesAPIView.as_view(), name='componentes_api'),
    path('api/estructuras-proyecto/', views.EstructurasProyectoAPIView.as_view(), name='estructuras_proyecto_api'),
] 