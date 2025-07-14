from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.main import ListRegistrosView
from .views.registros import RegistrosTxTssViewSet
from .views.r_sitio_view import RSitioView
from .views.steps import StepsRegistroView

app_name = "registrostxtss"

# Configurar el router para los ViewSets
router = DefaultRouter()
router.register(r'api/v1/registros', RegistrosTxTssViewSet, basename='registros')
# router.register(r'api/v1/rsitio', RSitioViewSet, basename='rsitio')

urlpatterns = [
    path("registrostxtss/", ListRegistrosView.as_view(), name="list"),
    path("a/<int:registro_id>/", RSitioView.as_view(), name="create"),
    path("registrostxtss/<int:registro_id>/", StepsRegistroView.as_view(), name="create"),
    
    # Incluir las rutas del ViewSet
    path('', include(router.urls)),
]
