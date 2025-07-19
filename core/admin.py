from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from .models.sites import Site
from .models.registros import Registro
from .models.app_settings import AppSettings
from import_export.formats.base_formats import CSV, XLSX

class SiteResource(resources.ModelResource):
    pti_cell_id = fields.Field(attribute='pti_cell_id', column_name='PTI ID')
    operator_id = fields.Field(attribute='operator_id', column_name='Operador ID')
    nombre_sitio = fields.Field(attribute='name', column_name='Nombre del Sitio')
    lat_base = fields.Field(attribute='lat_base', column_name='Latitud Base')
    lon_base = fields.Field(attribute='lon_base', column_name='Longitud Base')
    alt = fields.Field(attribute='alt', column_name='Altura (m)')
    region = fields.Field(attribute='region', column_name='Region / Provincia')
    comuna = fields.Field(attribute='comuna', column_name='Comuna / Municipio')

    class Meta:
        model = Site
        fields = ('pti_cell_id', 'operator_id', 'nombre_sitio', 'lat_base', 'lon_base', 'alt', 'region', 'comuna')
        import_id_fields = () 
        export_order = ('pti_cell_id', 'operator_id', 'nombre_sitio', 'lat_base', 'lon_base', 'alt', 'region', 'comuna')
        import_id_fields = ('pti_cell_id',)

class SiteAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = SiteResource
    list_display = ('pti_cell_id', 'operator_id', 'name', 'alt', 'region', 'comuna', 'is_deleted')
    list_editable = ('is_deleted',)
    ordering = ('pti_cell_id',)
    list_display_links = ('name',)
    list_per_page = 100
    
    def get_export_formats(self):
        return [CSV(), XLSX()]
    
admin.site.register(Site, SiteAdmin)

class RegistroAdmin(admin.ModelAdmin):
    list_display = ('id', 'sitio', 'created_at', 'is_deleted')
    ordering = ('sitio',)
    list_per_page = 100

admin.site.register(Registro, RegistroAdmin)

class AppSettingsAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'google_maps_api_key', 'last_apk_version', 'created_at')
    list_editable = ('google_maps_api_key', 'last_apk_version')
    search_fields = ('app_name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información General', {
            'fields': ('app_name', 'logo')
        }),
        ('Google Maps', {
            'fields': ('google_maps_api_key',),
            'description': 'Configura la API key de Google Maps para generar imágenes de mapas estáticos.'
        }),
        ('APK', {
            'fields': ('app_apk', 'last_apk_version'),
            'description': 'Configuración para la aplicación móvil APK.'
        }),
        ('Notificaciones', {
            'fields': ('recipients_email',),
            'description': 'Lista de correos electrónicos separados por comas para recibir notificaciones.'
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        # Solo mostrar la configuración más reciente
        return super().get_queryset(request).order_by('-created_at')[:1]

admin.site.register(AppSettings, AppSettingsAdmin)