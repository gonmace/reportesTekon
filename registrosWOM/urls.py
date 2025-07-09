from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.list import ListRegistrosView, RegistrosViewSet

app_name = "registrosWOM"

router = DefaultRouter()
router.register(r'registros', RegistrosViewSet, basename='registros')

urlpatterns = [
    path("registrosWOM/", ListRegistrosView.as_view(), name="list"),
    path("api/v1/", include(router.urls)),
    # path("registrosWOM/create/<int:pk>/", CreateRegistro0View.as_view(), name="create"),
]
