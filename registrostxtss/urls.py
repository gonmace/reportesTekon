from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.main import ListRegistrosView
from .views.registros import RegistrosTxTssViewSet

app_name = "registrostxtss"

# Configurar el router para el ViewSet
router = DefaultRouter()
router.register(r'api/v1/registros', RegistrosTxTssViewSet, basename='registros')

urlpatterns = [
    path("registrostxtss/", ListRegistrosView.as_view(), name="list"),
    
    # Incluir las rutas del ViewSet
    path('', include(router.urls)),
]
