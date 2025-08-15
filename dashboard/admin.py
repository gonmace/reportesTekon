from django.contrib import admin
from django.utils.html import format_html
from .models import DashboardMetric, SitioDashboard

@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_type', 'value', 'last_updated']
    list_filter = ['metric_type', 'last_updated']
    readonly_fields = ['last_updated']
    search_fields = ['metric_type']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('metric_type',)
        return self.readonly_fields

@admin.register(SitioDashboard)
class SitioDashboardAdmin(admin.ModelAdmin):
    list_display = [
        'sitio', 'total_registros_txtss', 'total_registros_construccion', 
        'estado_actual', 'ultimo_registro_txtss', 'ultimo_registro_construccion', 
        'last_updated'
    ]
    list_filter = ['estado_actual', 'last_updated', 'sitio__region']
    readonly_fields = ['last_updated']
    search_fields = ['sitio__name', 'sitio__pti_cell_id']
    list_select_related = ['sitio']
    
    def sitio_link(self, obj):
        if obj.sitio:
            return format_html(
                '<a href="{}">{}</a>',
                f'/admin/core/site/{obj.sitio.id}/change/',
                obj.sitio.name
            )
        return "Sin sitio"
    sitio_link.short_description = 'Sitio'
    sitio_link.admin_order_field = 'sitio__name'
    
    def ultimo_registro_txtss_formatted(self, obj):
        if obj.ultimo_registro_txtss:
            return obj.ultimo_registro_txtss.strftime('%d/%m/%Y %H:%M')
        return "N/A"
    ultimo_registro_txtss_formatted.short_description = 'Último TXTSS'
    
    def ultimo_registro_construccion_formatted(self, obj):
        if obj.ultimo_registro_construccion:
            return obj.ultimo_registro_construccion.strftime('%d/%m/%Y %H:%M')
        return "N/A"
    ultimo_registro_construccion_formatted.short_description = 'Último Construcción'
    
    actions = ['update_metrics']
    
    def update_metrics(self, request, queryset):
        updated = 0
        for sitio_dashboard in queryset:
            sitio_dashboard.update_metrics()
            updated += 1
        
        self.message_user(
            request,
            f'Se actualizaron las métricas de {updated} sitio(s).'
        )
    update_metrics.short_description = "Actualizar métricas de sitios seleccionados"
