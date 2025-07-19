from django.urls import path, include
from .views import ListRegistrosView, StepsRegistroView
from .r_sitio.views import RSitioView
from .r_acceso.views import RAccesoView
from .r_empalme.views import REmpalmeView

app_name = "registros_txtss"

urlpatterns = [
    path("registros/", ListRegistrosView.as_view(), name="list"),
    path("registros/<int:registro_id>/", StepsRegistroView.as_view(), name="steps"),
    path("registros/<int:registro_id>/sitio/", RSitioView.as_view(), name="r_sitio"),
    path("registros/<int:registro_id>/acceso/", RAccesoView.as_view(), name="r_acceso"),
    path("registros/<int:registro_id>/empalme/", REmpalmeView.as_view(), name="r_empalme"),
    # Incluir URLs de fotos
    path("registros/", include("photos.urls")),
] 