from django.urls import path
from .views import (
    ListRegistrosView,
    StepsRegistroView,
    ElementoRegistroView,
    ActivarRegistroView,
    TableOnlyView,
)
from .pdf_views import RegConstruccionPDFView, preview_reg_construccion_individual

app_name = 'reg_construccion'

urlpatterns = [
    path('', ListRegistrosView.as_view(), name='list'),
    path('activar/', ActivarRegistroView.as_view(), name='activar'),
    path('<int:registro_id>/', StepsRegistroView.as_view(), name='steps'),
    path('<int:registro_id>/<str:paso_nombre>/', ElementoRegistroView.as_view(), name='elemento'),
    path('<int:registro_id>/<str:paso_nombre>/tabla/', TableOnlyView.as_view(), name='elemento_tabla'),
    path('pdf/<int:registro_id>/', RegConstruccionPDFView.as_view(), name='pdf'),
    path('preview/<int:registro_id>/', preview_reg_construccion_individual, name='preview'),
]