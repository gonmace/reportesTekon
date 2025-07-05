from django.urls import path

from core.views.sitios import SitiosView, SitiosAPIView, SiteEditView, SiteDeleteView

app_name = "sitios"

urlpatterns = [
    path("", SitiosView.as_view(), name="sitios_list"),
    path("api/", SitiosAPIView.as_view(), name="sitios_api"),
    path('<int:pk>/editar/', SiteEditView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', SiteDeleteView.as_view(), name='eliminar'),
]
