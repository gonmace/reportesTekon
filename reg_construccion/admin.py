"""
Admin para registros Reporte de construcción.
"""

from django.contrib import admin
from .models import RegConstruccion, AvanceComponente, EjecucionPorcentajes, Objetivo


@admin.register(RegConstruccion)
class RegConstruccionAdmin(admin.ModelAdmin):
    list_display = ['id', 'sitio', 'user', 'estructura', 'title', 'created_at']
    list_filter = ['created_at', 'estructura']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Objetivo)
class ObjetivoAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'objetivo', 'created_at']
    list_filter = ['created_at', 'registro']
    search_fields = ['objetivo']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AvanceComponente)
class AvanceComponenteAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'componente', 'fecha', 'porcentaje_actual', 'porcentaje_acumulado', 'created_at']
    list_filter = ['fecha', 'componente', 'registro']
    search_fields = ['comentarios']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EjecucionPorcentajes)
class EjecucionPorcentajesAdmin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'componente', 'porcentaje_ejec_actual', 'porcentaje_ejec_anterior', 'fecha_calculo']
    list_filter = ['fecha_calculo', 'componente', 'registro']
    readonly_fields = ['fecha_calculo']
    ordering = ['-fecha_calculo']
    list_per_page = 50

