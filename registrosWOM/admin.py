from django.contrib import admin
from .models import Registros0

@admin.register(Registros0)
class Registros0Admin(admin.ModelAdmin):
    list_display = ['sitio', 'fecha', 'descripcion']
    list_filter = ['fecha']
    search_fields = ['sitio', 'descripcion']
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
