from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegistroInicialView, NuevoRegistroView

app_name = "registro_inicial"

# router = DefaultRouter()
# router.register(r'sitios', SiteViewSet, basename='sitios')

urlpatterns = [
    path("", RegistroInicialView.as_view(), name="list"),
    path("nuevo/", NuevoRegistroView.as_view(), name="nuevo"),
    # path('api/v1/', include(router.urls)),
    # path('api/v1/sitios/<int:site_id>/edit-modal/', SiteEditModalView.as_view(), name='site_edit_modal'),
]
