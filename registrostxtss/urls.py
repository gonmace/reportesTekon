from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.main import ListRegistrosView
from .views.registros import RegistrosTxTssViewSet
from .views.steps import StepsRegistroView

from .r_sitio.views import RSitioView

app_name = "registrostxtss"

# Configurar el router para los ViewSets
router = DefaultRouter()
router.register(r'api/v1/registros', RegistrosTxTssViewSet, basename='registros')
# router.register(r'api/v1/rsitio', RSitioViewSet, basename='rsitio')

urlpatterns = [
    path("registrostxtss/", ListRegistrosView.as_view(), name="list"),
    
    path("registrostxtss/<int:registro_id>/", StepsRegistroView.as_view(), name="steps"),
    path("registrostxtss/<int:registro_id>/<str:title>", RSitioView.as_view(), name="sitio"),
    
    path("registrostxtss/", include("photos.urls"), name="photos"),
    
    # Incluir las rutas del ViewSet
    path('', include(router.urls)),
]
