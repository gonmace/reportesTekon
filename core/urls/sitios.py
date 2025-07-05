from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views.sitios import SitiosView, SitiosAPIView, SiteEditView, SiteViewSet

app_name = "sitios"

router = DefaultRouter()
router.register(r'sitios', SiteViewSet, basename='sitios')

urlpatterns = [
    path("sitios/", SitiosView.as_view(), name="sitios_list"),
    path('api/v1/', include(router.urls)),
]
