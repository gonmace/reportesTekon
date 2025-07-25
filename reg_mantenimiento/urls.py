"""
URLs para registros Mantenimiento Preventivo.
"""

from django.urls import path
from .views import ListRegistrosView, StepsRegistroView, ElementoRegistroView, ActivarRegistroView

app_name = 'reg_mantenimiento'

urlpatterns = [
    path('', ListRegistrosView.as_view(), name='list'),
    path('<int:registro_id>/steps/', StepsRegistroView.as_view(), name='steps'),
    path('<int:registro_id>/<str:paso_nombre>/', ElementoRegistroView.as_view(), name='elemento'),
    path('<int:registro_id>/activar/', ActivarRegistroView.as_view(), name='activar'),
]