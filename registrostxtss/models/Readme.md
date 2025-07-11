# Crear un registro
registro = Registros0.objects.create(
    sitio=site,
    lat=-33.4567,
    lon=-70.6483,
    altura="100m",
    dimensiones="10x20m",
    deslindes="Norte: Calle Principal"
)
# created_at se establece automáticamente

# Obtener solo registros activos
registros_activos = Registros0.get_actives()

# Soft delete
registro.soft_delete()
# is_deleted = True, deleted_at = now