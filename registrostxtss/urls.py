from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.main import ListRegistrosView
from .views.registros import RegistrosTxTssViewSet
from .views.create import CreateRegistroView
from .views.steps import StepsRegistroView
app_name = "registrostxtss"

# Configurar el router para los ViewSets
router = DefaultRouter()
router.register(r'api/v1/registros', RegistrosTxTssViewSet, basename='registros')
# router.register(r'api/v1/registros0', Registros0ViewSet, basename='registros0')

urlpatterns = [
    path("registrostxtss/", ListRegistrosView.as_view(), name="list"),
    # path("registrostxtss/<int:registro_id>/", CreateRegistroView.as_view(), name="create"),
    path("registrostxtss/<int:registro_id>/", StepsRegistroView.as_view(), name="create"),
    
    # Incluir las rutas del ViewSet
    path('', include(router.urls)),
]
