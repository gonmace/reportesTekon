"""
Admin para registros reg_mantenimiento.
"""

from django.contrib import admin
from .models import RegMantenimiento, Inspeccion, Diagnostico, Reparacion, Pruebas, Verificacion

@admin.register(RegMantenimiento)
class RegMantenimientoAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'sitio', 'user', 'created_at']
    list_filter = ['created_at', 'sitio']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Inspeccion)
class InspeccionAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comentarios']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comentarios']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Reparacion)
class ReparacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comentarios']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Pruebas)
class PruebasAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comentarios']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Verificacion)
class VerificacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comentarios']
    readonly_fields = ['created_at', 'updated_at']

