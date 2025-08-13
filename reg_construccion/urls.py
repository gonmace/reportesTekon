from django.urls import path, include
from .views import (
    ListRegistrosView,
    StepsRegistroView,
    ElementoRegistroView,
    ActivarRegistroView,
    TableOnlyView,
    guardar_ejecucion,
    actualizar_ejecucion_ajax,
    RegConstruccionCreateView,
    RegConstruccionUpdateView,
    RegConstruccionDeleteView,
    dashboard_construccion,
    update_contratista,
)
from .pdf_views import RegConstruccionPDFView, preview_reg_construccion_individual

app_name = 'reg_construccion'

urlpatterns = [
    path('', ListRegistrosView.as_view(), name='list'),
    path('dashboard/', dashboard_construccion, name='dashboard'),
    path('activar/', ActivarRegistroView.as_view(), name='activar'),
    path('crear/', RegConstruccionCreateView.as_view(), name='create'),
    path('<int:registro_id>/', StepsRegistroView.as_view(), name='steps'),
    path('<int:registro_id>/editar/', RegConstruccionUpdateView.as_view(), name='update'),
    path('<int:registro_id>/eliminar/', RegConstruccionDeleteView.as_view(), name='delete'),
    path('<int:registro_id>/update-contratista/', update_contratista, name='update_contratista'),
    path('<int:registro_id>/<str:paso_nombre>/', ElementoRegistroView.as_view(), name='elemento'),
    path('<int:registro_id>/<str:paso_nombre>/tabla/', TableOnlyView.as_view(), name='elemento_tabla'),
    path('guardar-ejecucion/<int:registro_id>/', guardar_ejecucion, name='guardar_ejecucion'),
    path('actualizar-ejecucion/<int:registro_id>/', actualizar_ejecucion_ajax, name='actualizar_ejecucion_ajax'),
    path('pdf/<int:registro_id>/', RegConstruccionPDFView.as_view(), name='pdf'),
    path('preview/<int:registro_id>/', preview_reg_construccion_individual, name='preview'),
    
    # URLs de photos específicas para reg_construccion
    path('<int:registro_id>/<str:step_name>/photos/', include('photos.urls')),
]