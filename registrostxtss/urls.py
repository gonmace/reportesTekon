from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.main import ListRegistrosView
from .views.registros import RegistrosTxTssViewSet
from .views import StepsRegistroView
from .views.reports import (
    reports_dashboard, 
    generate_complete_pdf_report, 
    generate_summary_pdf_report,
    reports_list,
    generate_custom_report
)

from .r_sitio.views import RSitioView
from .r_acceso.views import RAccesoView
from .r_empalme.views import REmpalmeView

app_name = "registrostxtss"

# Configurar el router para los ViewSets
router = DefaultRouter()
router.register(r'api/v1/registros', RegistrosTxTssViewSet, basename='registros')
# router.register(r'api/v1/rsitio', RSitioViewSet, basename='rsitio')

urlpatterns = [
    path("registrostxtss/", ListRegistrosView.as_view(), name="list"),
    
    path("registrostxtss/<int:registro_id>/", StepsRegistroView.as_view(), name="steps"),
    path("registrostxtss/<int:registro_id>/sitio/", RSitioView.as_view(), name="r_sitio"),
    path("registrostxtss/<int:registro_id>/acceso/", RAccesoView.as_view(), name="r_acceso"),
    path("registrostxtss/<int:registro_id>/empalme/", REmpalmeView.as_view(), name="r_empalme"),
    
    # URLs para informes
    path("registrostxtss/reports/", reports_dashboard, name="reports_dashboard"),
    path("registrostxtss/reports/list/", reports_list, name="reports_list"),
    path("registrostxtss/reports/pdf/complete/", generate_complete_pdf_report, name="generate_complete_pdf"),
    path("registrostxtss/reports/pdf/summary/", generate_summary_pdf_report, name="generate_summary_pdf"),
    path("registrostxtss/reports/pdf/custom/", generate_custom_report, name="generate_custom_pdf"),
    
    path("registrostxtss/", include("photos.urls"), name="photos"),
    
    # Incluir las rutas del ViewSet
    path('', include(router.urls)),
]
