from django.contrib import admin
from .models import RSitio


@admin.register(RSitio)
class RSitioAdmin(admin.ModelAdmin):
    list_display = ['registro', 'lat', 'lon', 'dimensiones', 'altura', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['registro__nombre', 'dimensiones', 'altura']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información del Registro', {
            'fields': ('registro',)
        }),
        ('Coordenadas', {
            'fields': ('lat', 'lon')
        }),
        ('Características del Sitio', {
            'fields': ('dimensiones', 'altura', 'deslindes')
        }),
        ('Información Adicional', {
            'fields': ('comentarios',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ) 