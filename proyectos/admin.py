"""
Configuración del admin para la aplicación de proyectos.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Avg
from .models import Componente, GrupoComponentes, ComponenteGrupo


class ComponenteGrupoInline(admin.TabularInline):
    model = ComponenteGrupo
    extra = 0
    fields = ['componente', 'incidencia']


@admin.register(Componente)
class ComponenteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'num_grupos']
    search_fields = ['nombre']
    ordering = ['nombre']
    
    def num_grupos(self, obj):
        return obj.componentegrupo_set.count()
    num_grupos.short_description = 'Grupos'


@admin.register(GrupoComponentes)
class GrupoComponentesAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'num_componentes', 'porcentaje_incidencia_total']
    search_fields = ['nombre']
    ordering = ['nombre']
    inlines = [ComponenteGrupoInline]
    
    def num_componentes(self, obj):
        return obj.componentes.count()
    num_componentes.short_description = 'Componentes'
    
    def porcentaje_incidencia_total(self, obj):
        total = obj.componentes.aggregate(total=Sum('incidencia'))['total'] or 0
        return f"{total}%"
    porcentaje_incidencia_total.short_description = '% Incidencia Total'


@admin.register(ComponenteGrupo)
class ComponenteGrupoAdmin(admin.ModelAdmin):
    list_display = ['grupo', 'componente', 'incidencia']
    list_filter = ['grupo', 'componente']
    search_fields = ['grupo__nombre', 'componente__nombre']
    ordering = ['grupo', 'componente']
    
    def incidencia(self, obj):
        return f"{obj.incidencia}%"
    incidencia.short_description = '% Incidencia'
