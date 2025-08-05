"""
Admin para registros reg_construccion.
"""

from django.contrib import admin
from .models import RegConstruccion, Visita, Avance

@admin.register(RegConstruccion)
class RegConstruccionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'sitio', 'user', 'created_at']
    list_filter = ['created_at', 'sitio']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comentarios']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Avance)
class AvanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comentarios']
    readonly_fields = ['created_at', 'updated_at']

