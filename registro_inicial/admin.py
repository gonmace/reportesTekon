from django.contrib import admin
from .models import RegistroInicial

@admin.register(RegistroInicial)
class RegistroInicialAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha', 'creado_por', 'fecha_creacion']
    list_filter = ['fecha', 'fecha_creacion', 'creado_por']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['creado_por', 'fecha_creacion', 'fecha_actualizacion']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
