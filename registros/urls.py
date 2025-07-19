from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.registros import RegistrosViewSet
from .views.google_maps import GoogleMapsView

app_name = "registros"

# Configurar el router para los ViewSets
router = DefaultRouter()
router.register(r'api/v1/registros', RegistrosViewSet, basename='registros')

urlpatterns = [
    path("registros/", include("photos.urls"), name="photos"),
    
    # API endpoint para Google Maps
    path('api/v1/google-maps/', GoogleMapsView.as_view(), name='google_maps'),
    
    # Incluir las rutas del ViewSet
    path('', include(router.urls)),
]
