"""
Admin para registros Reporte de construcción.
"""

from django.contrib import admin
from .models import RegConstruccion, Visita, AvanceComponente


@admin.register(RegConstruccion)
class RegConstruccionAdmin(admin.ModelAdmin):
    list_display = ['id', 'sitio', 'user', 'estructura', 'title', 'created_at']
    list_filter = ['created_at', 'estructura']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comentarios']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AvanceComponente)
class AvanceComponenteAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'componente', 'fecha', 'porcentaje_actual', 'porcentaje_acumulado', 'created_at']
    list_filter = ['fecha', 'created_at', 'componente', 'porcentaje_actual', 'porcentaje_acumulado']
    search_fields = ['comentarios', 'componente__nombre']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-fecha', '-created_at']

