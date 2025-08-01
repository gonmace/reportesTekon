"""
Admin para registros reg_visita.
"""

from django.contrib import admin
from .models import RegVisita, AvanceProyecto

@admin.register(RegVisita)
class RegVisitaAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'sitio', 'user', 'created_at']
    list_filter = ['created_at', 'sitio']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AvanceProyecto)
class AvanceProyectoAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'proyecto', 'componente', 'ejecucion_actual', 'ejecucion_total', 'created_at']
    list_filter = ['created_at', 'proyecto', 'componente']
    search_fields = ['proyecto__nombre', 'componente__nombre', 'comentarios']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información General', {
            'fields': ('registro', 'proyecto', 'componente')
        }),
        ('Comentarios', {
            'fields': ('comentarios',)
        }),
        ('Porcentajes de Ejecución', {
            'fields': ('ejecucion_anterior', 'ejecucion_actual', 'ejecucion_acumulada', 'ejecucion_total')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

