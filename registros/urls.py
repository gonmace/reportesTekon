from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.main import ListRegistrosView
from .views.registros import RegistrosViewSet
from .views import StepsRegistroView
from .views.google_maps import GoogleMapsView

from .r_sitio.views import RSitioView
from .r_acceso.views import RAccesoView
from .r_empalme.views import REmpalmeView

app_name = "registros"

# Configurar el router para los ViewSets
router = DefaultRouter()
router.register(r'api/v1/registros', RegistrosViewSet, basename='registros')
# router.register(r'api/v1/rsitio', RSitioViewSet, basename='rsitio')

urlpatterns = [
    path("registros/", ListRegistrosView.as_view(), name="list"),
    
    path("registros/<int:registro_id>/", StepsRegistroView.as_view(), name="steps"),
    path("registros/<int:registro_id>/sitio/", RSitioView.as_view(), name="r_sitio"),
    path("registros/<int:registro_id>/acceso/", RAccesoView.as_view(), name="r_acceso"),
    path("registros/<int:registro_id>/empalme/", REmpalmeView.as_view(), name="r_empalme"),
    
    path("registros/", include("photos.urls"), name="photos"),
    
    # API endpoint para Google Maps
    path('api/v1/google-maps/', GoogleMapsView.as_view(), name='google_maps'),
    
    # Incluir las rutas del ViewSet
    path('', include(router.urls)),
]
