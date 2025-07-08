from django.contrib import admin
from .models.registro import Registros

@admin.register(Registros)
class RegistrosAdmin(admin.ModelAdmin):
    list_display = ['sitio', 'registro0', 'registro1', 'registro2']
    list_filter = ['registro0', 'registro1', 'registro2']
    search_fields = ['sitio', 'registro0', 'registro1', 'registro2']
    readonly_fields = ['sitio', 'created_at', 'updated_at']
