from django.contrib import admin
from django.utils.html import format_html
from admin_sort.admin import SortableAdminMixin
from .models import Componente, Grupo, EstructuraProyecto


class ComponenteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']
    ordering = ['nombre']
    
    def delete_model(self, request, obj):
        """Eliminar el componente y todos los registros relacionados"""
        try:
            # Mostrar información sobre lo que se va a eliminar
            from proyectos.models import EstructuraProyecto
            from reg_visita.models import AvanceProyecto
            
            estructuras_count = EstructuraProyecto.objects.filter(componente=obj).count()
            avances_count = AvanceProyecto.objects.filter(componente=obj).count()
            
            from django.contrib import messages
            if estructuras_count > 0 or avances_count > 0:
                messages.warning(request, 
                    f'Se eliminarán {estructuras_count} estructuras de proyecto y {avances_count} avances relacionados con el componente "{obj.nombre}"')
            
            # El signal se encargará de eliminar los registros relacionados
            obj.delete()
            
            messages.success(request, f'Componente "{obj.nombre}" eliminado exitosamente')
            
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error al eliminar el componente: {str(e)}')
            raise
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminación"""
        return True

class GrupoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'get_componentes_count', 'get_total_incidencia', 'get_proyectos_count', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']
    ordering = ['nombre']
    
    def get_componentes_count(self, obj):
        """Muestra el número de componentes en el grupo"""
        count = obj.componentes.count()
        return f"{count} componente{'s' if count != 1 else ''}"
    get_componentes_count.short_description = 'Componentes'
    get_componentes_count.admin_order_field = 'componentes__count'
    
    def get_total_incidencia(self, obj):
        """Muestra el total de incidencia del grupo"""
        total = sum(inc.incidencia for inc in obj.estructuraproyecto_set.all())
        color = 'green' if total == 100 else 'orange' if total >= 90 else 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}%</span>', color, total)
    get_total_incidencia.short_description = 'Total Incidencia'
    
    def get_proyectos_count(self, obj):
        """Muestra el número de proyectos que usan este grupo"""
        # Comentado temporalmente hasta que se defina la relación
        return "0 proyectos"
    get_proyectos_count.short_description = 'Proyectos'
    
    def get_queryset(self, request):
        """Optimizar las consultas"""
        return super().get_queryset(request).prefetch_related('componentes', 'estructuraproyecto_set')

class EstructuraProyectoAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['grupo', 'componente', 'incidencia', 'activo']
    list_filter = ['grupo', 'activo']
    search_fields = ['grupo__nombre', 'componente__nombre']
    list_editable = ['incidencia', 'activo']
    ordering = ['grupo', 'sort_order', 'orden']
    position_field = 'sort_order'
    
    def get_queryset(self, request):
        """Optimizar las consultas"""
        return super().get_queryset(request).select_related('grupo', 'componente')





# Registrar los modelos en el admin principal
admin.site.register(Componente, ComponenteAdmin)
admin.site.register(Grupo, GrupoAdmin)
admin.site.register(EstructuraProyecto, EstructuraProyectoAdmin)
# admin.site.register(Proyecto, ProyectoAdmin)  # Comentado temporalmente
