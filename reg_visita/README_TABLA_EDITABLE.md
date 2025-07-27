# Tablas Editables en reg_visita

Esta implementación permite crear elementos principales que son tablas editables con AJAX en lugar de formularios tradicionales.

## 🎯 Características

- **Edición inline**: Haga clic en cualquier celda editable para modificarla directamente
- **Operaciones CRUD completas**: Crear, leer, actualizar y eliminar registros
- **Validación en tiempo real**: Validación del lado del cliente y servidor
- **Interfaz intuitiva**: Modal para agregar/editar registros completos
- **Paginación**: Navegación entre páginas de registros
- **Permisos**: Control de acceso basado en roles de usuario

## 🚀 Cómo usar

### 1. Acceder a las tablas editables

Las tablas editables están disponibles en las siguientes URLs:

- **Visitas**: `/reg_visita/visitas/`
- **Avances**: `/reg_visita/avances/`

### 2. Funcionalidades disponibles

#### Edición inline
1. Haga clic en cualquier celda editable (marcada con cursor de puntero)
2. Escriba el nuevo valor
3. Presione Enter para guardar o Escape para cancelar
4. El cambio se guarda automáticamente via AJAX

#### Agregar nuevo registro
1. Haga clic en el botón "Agregar Registro"
2. Complete el formulario en el modal
3. Haga clic en "Guardar"

#### Editar registro completo
1. Haga clic en el botón de editar (ícono de lápiz)
2. Modifique los campos en el modal
3. Haga clic en "Guardar"

#### Eliminar registro
1. Haga clic en el botón de eliminar (ícono de papelera)
2. Confirme la eliminación

## 🔧 Configuración

### Configuración de columnas

```python
# En config.py
visitas_columns = [
    {
        'key': 'comentarios',        # Campo del modelo
        'label': 'Comentarios',      # Etiqueta mostrada
        'type': 'text',              # Tipo de campo
        'editable': True,            # Si es editable
        'required': True             # Si es requerido
    },
    {
        'key': 'created_at',
        'label': 'Fecha Creación',
        'type': 'text',
        'editable': False            # Solo lectura
    }
]
```

### Configuración de tabla

```python
# En config.py
'visita': create_table_only_config(
    title='Visitas',
    description='Administre las visitas realizadas.',
    columns=visitas_columns,
    model_class=Visita,
    template_name='components/editable_table.html',
    api_url='/reg_visita/api/visitas/',
    allow_create=True,
    allow_edit=True,
    allow_delete=True,
    page_length=10
)
```

## 📁 Archivos creados/modificados

### Nuevos archivos:
- `registros/config.py` - Funciones de configuración para tablas editables
- `templates/components/editable_table.html` - Template principal para tablas editables
- `templates/components/table_only.html` - Template para pasos con solo tablas
- `registros/components/editable_table.py` - Componente para manejar tablas editables
- `reg_visita/views.py` - Vistas API y de tabla editable
- `reg_visita/urls.py` - URLs para las nuevas vistas

### Archivos modificados:
- `reg_visita/config.py` - Configuración actualizada para usar tablas editables
- `registros/components/registro_config.py` - Soporte para tablas editables

## 🔌 API Endpoints

### Visitas
- `GET /reg_visita/api/visitas/` - Obtener todas las visitas
- `POST /reg_visita/api/visitas/` - Crear nueva visita
- `PUT /reg_visita/api/visitas/{id}/` - Actualizar visita completa
- `PATCH /reg_visita/api/visitas/{id}/` - Actualizar campo específico
- `DELETE /reg_visita/api/visitas/{id}/` - Eliminar visita

### Avances
- `GET /reg_visita/api/avances/` - Obtener todos los avances
- `POST /reg_visita/api/avances/` - Crear nuevo avance
- `PUT /reg_visita/api/avances/{id}/` - Actualizar avance completo
- `PATCH /reg_visita/api/avances/{id}/` - Actualizar campo específico
- `DELETE /reg_visita/api/avances/{id}/` - Eliminar avance

## 🎨 Personalización

### Agregar nuevos tipos de campos

```python
# En la configuración de columnas
{
    'key': 'estado',
    'label': 'Estado',
    'type': 'select',
    'editable': True,
    'options': [
        {'value': 'pendiente', 'label': 'Pendiente'},
        {'value': 'en_proceso', 'label': 'En Proceso'},
        {'value': 'completado', 'label': 'Completado'}
    ]
}
```

### Cambiar estilos

Modifique el CSS en `templates/components/editable_table.html`:

```css
.editable-cell {
    cursor: pointer;
    background-color: #f8f9fa;
}

.editable-cell:hover {
    background-color: #e9ecef;
}
```

## 🔒 Seguridad

- **CSRF Protection**: Todas las operaciones incluyen tokens CSRF
- **Permisos de usuario**: Solo los propietarios pueden editar sus registros
- **Validación**: Validación tanto del lado del cliente como del servidor
- **Soft Delete**: Los registros se marcan como eliminados en lugar de borrarse físicamente

## 🐛 Solución de problemas

### Error 403 - No tiene permisos
- Verifique que el usuario esté autenticado
- Asegúrese de que el usuario sea propietario del registro o superusuario

### Error 400 - Error al guardar
- Verifique que todos los campos requeridos estén completos
- Revise la consola del navegador para errores de JavaScript

### La tabla no se carga
- Verifique que la URL de la API sea correcta
- Revise los logs del servidor para errores de Django

## 📈 Próximas mejoras

- [ ] Búsqueda y filtros avanzados
- [ ] Exportación a Excel/CSV
- [ ] Ordenamiento por columnas
- [ ] Validación en tiempo real más avanzada
- [ ] Soporte para archivos adjuntos
- [ ] Historial de cambios 