from django.contrib import admin
from .models.main_registrostxtss import RegistrosTxTss
from .r_sitio.models import RSitio
from .r_acceso.models import RAcceso

admin.site.register(RegistrosTxTss)

admin.site.register(RSitio)

admin.site.register(RAcceso)
