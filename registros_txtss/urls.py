"""
URLs para registros TX/TSS.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListRegistrosView, StepsRegistroView, ElementoRegistroView, ActivarRegistroView
from registros.views.registros import RegistrosViewSet
from users.views import UserViewSet

app_name = "registros_txtss"

# API Router
router = DefaultRouter()
router.register(r'api/v1/registros', RegistrosViewSet, basename='registros')
router.register(r'api/v1/usuarios', UserViewSet, basename='usuarios')

urlpatterns = [
    # Vistas principales
    path("", ListRegistrosView.as_view(), name="list"),
    path("activar/", ActivarRegistroView.as_view(), name="activar_registro"),
    path("registros/<int:registro_id>/", StepsRegistroView.as_view(), name="steps"),
    path("registros/<int:registro_id>/<str:paso_nombre>/", ElementoRegistroView.as_view(), name="elemento"),
    
    # API URLs
    path("", include(router.urls)),
] 