"""
Configuración del admin para la aplicación de proyectos.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Avg
from .models import Componente, Grupo, GrupoComponente


class GrupoComponenteInline(admin.TabularInline):
    model = GrupoComponente
    extra = 0
    fields = ['componente', 'porcentaje_incidencia', 'orden', 'activo']


@admin.register(Componente)
class ComponenteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion_corta', 'num_grupos']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    
    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    
    def num_grupos(self, obj):
        return obj.grupos_componente.count()
    num_grupos.short_description = 'Grupos'


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion_corta', 'num_componentes', 'porcentaje_incidencia_total', 'activo']
    list_filter = ['activo', 'orden']
    search_fields = ['nombre', 'descripcion']
    ordering = ['orden', 'nombre']
    inlines = [GrupoComponenteInline]
    
    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    
    def num_componentes(self, obj):
        return obj.componentes_grupo.count()
    num_componentes.short_description = 'Componentes'
    
    def porcentaje_incidencia_total(self, obj):
        return f"{obj.porcentaje_incidencia_total}%"
    porcentaje_incidencia_total.short_description = '% Incidencia Total'


@admin.register(GrupoComponente)
class GrupoComponenteAdmin(admin.ModelAdmin):
    list_display = ['grupo', 'componente', 'porcentaje_incidencia', 'orden', 'activo']
    list_filter = ['activo', 'orden', 'grupo', 'componente']
    search_fields = ['grupo__nombre', 'componente__nombre']
    ordering = ['grupo', 'orden']
    
    def porcentaje_incidencia(self, obj):
        return f"{obj.porcentaje_incidencia}%"
    porcentaje_incidencia.short_description = '% Incidencia'
