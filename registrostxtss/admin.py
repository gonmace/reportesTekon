from django.contrib import admin
from .models.registrostxtss import RegistrosTxTss
from .r_sitio.models import RSitio
from .r_acceso.models import RAcceso
from .models.registrostxtss import MapasGoogle

admin.site.register(RegistrosTxTss)

admin.site.register(RSitio)

admin.site.register(RAcceso)

admin.site.register(MapasGoogle)
