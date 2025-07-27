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
    path('<int:registro_id>/steps/', views.StepsRegistroView.as_view(), name='steps'),
    path('<int:registro_id>/<str:paso_nombre>/', views.ElementoRegistroView.as_view(), name='elemento'),
    
    # URLs para tablas editables
    path('api/visitas/', views.VisitaTableAPIView.as_view(), name='visitas_api'),
    path('api/visitas/<int:pk>/', views.VisitaTableAPIView.as_view(), name='visitas_api_detail'),
    path('api/avances/', views.AvanceTableAPIView.as_view(), name='avances_api'),
    path('api/avances/<int:pk>/', views.AvanceTableAPIView.as_view(), name='avances_api_detail'),
    
    # URLs para vistas de tabla editable
    path('visitas/', views.VisitaTableView.as_view(), name='visitas'),
    path('avances/', views.AvanceTableView.as_view(), name='avances'),
]