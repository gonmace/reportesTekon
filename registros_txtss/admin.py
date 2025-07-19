from django.contrib import admin
from .r_sitio.models import RSitio
from .r_acceso.models import RAcceso
from .r_empalme.models import REmpalme

admin.site.register(RSitio)
admin.site.register(RAcceso)
admin.site.register(REmpalme)
