from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from .models.sites import Site
from .models.registros import Registro

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
    
admin.site.register(Site, SiteAdmin)

class RegistroAdmin(admin.ModelAdmin):
    list_display = ('id', 'sitio', 'created_at', 'is_deleted')
    ordering = ('sitio',)
    list_per_page = 100

admin.site.register(Registro, RegistroAdmin)