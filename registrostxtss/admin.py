from django.contrib import admin
from .models.main_registrostxtss import RegistrosTxTss
from .r_sitio.models import RSitio
admin.site.register(RegistrosTxTss)

admin.site.register(RSitio)
