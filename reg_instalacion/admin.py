"""
Admin para registros reg_instalacion.
"""

from django.contrib import admin
from .models import RegInstalacion, Sitio, Acceso, Empalme

@admin.register(RegInstalacion)
class RegInstalacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'sitio', 'user', 'created_at']
    list_filter = ['created_at', 'sitio']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Sitio)
class SitioAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comentarios']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Acceso)
class AccesoAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comentarios']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Empalme)
class EmpalmeAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comentarios']
    readonly_fields = ['created_at', 'updated_at']

