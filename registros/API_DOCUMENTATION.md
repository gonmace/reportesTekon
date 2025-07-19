# API de Registros Tx/Tss

Esta documentación describe los endpoints disponibles para la API de Registros Tx/Tss.

## Autenticación

Todos los endpoints requieren autenticación. Asegúrate de incluir el token de autenticación en el header:

```
Authorization: Token <tu_token>
```

## Endpoints Disponibles

### ViewSet Completo (RegistrosTxTssViewSet)

Todos los endpoints están manejados por un único ViewSet que proporciona funcionalidad completa.

#### Endpoints Básicos CRUD
- **Listar**: `GET /api/registros/`
- **Crear**: `POST /api/registros/`
- **Obtener**: `GET /api/registros/<id>/`
- **Actualizar**: `PUT /api/registros/<id>/`
- **Eliminar**: `DELETE /api/registros/<id>/`

#### Endpoints Personalizados

**Activar Registro**:
- **URL**: `PUT /api/registros/<id>/activar/`
- **Descripción**: Activa un registro específico

**Filtrar por Sitio (Query Params)**:
- **URL**: `GET /api/registros/por_sitio/?sitio_id=1`
- **Descripción**: Filtra registros por sitio usando query parameters

**Filtrar por Usuario (Query Params)**:
- **URL**: `GET /api/registros/por_usuario/?user_id=1`
- **Descripción**: Filtra registros por usuario usando query parameters

**Registros Activos**:
- **URL**: `GET /api/registros/activos/`
- **Descripción**: Obtiene solo registros activos

**Registros Inactivos**:
- **URL**: `GET /api/registros/inactivos/`
- **Descripción**: Obtiene solo registros inactivos

**Registros por Sitio (URL Path)**:
- **URL**: `GET /api/registros/sitio/<sitio_id>/`
- **Descripción**: Obtiene registros de un sitio específico usando URL path

**Registros por Usuario (URL Path)**:
- **URL**: `GET /api/registros/usuario/<user_id>/`
- **Descripción**: Obtiene registros de un usuario específico usando URL path

#### Filtros y Búsqueda

**Búsqueda**:
- `?search=nombre_sitio` - Buscar por nombre de sitio o usuario

**Ordenamiento**:
- `?ordering=created_at` - Ordenar por fecha de creación
- `?ordering=-created_at` - Ordenar por fecha de creación descendente
- `?ordering=sitio__name` - Ordenar por nombre de sitio

## Estructura del ViewSet

```python
class RegistrosTxTssViewSet(viewsets.ModelViewSet):
    # Maneja automáticamente todas las operaciones CRUD
    # Incluye endpoints personalizados con @action decorator
    
    @action(detail=True, methods=['put'])
    def activar(self, request, pk=None)
    
    @action(detail=False, methods=['get'])
    def por_sitio(self, request)
    
    @action(detail=False, methods=['get'])
    def por_usuario(self, request)
    
    @action(detail=False, methods=['get'])
    def activos(self, request)
    
    @action(detail=False, methods=['get'])
    def inactivos(self, request)
    
    @action(detail=False, methods=['get'])
    def sitio(self, request, sitio_id=None)
    
    @action(detail=False, methods=['get'])
    def usuario(self, request, user_id=None)
```

## Ejemplos de Uso

### Crear un nuevo registro
```bash
curl -X POST http://localhost:8000/api/registros/ \
  -H "Authorization: Token <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sitio_id": 1,
    "user_id": 1,
    "registro0": false
  }'
```

### Obtener todos los registros
```bash
curl -X GET http://localhost:8000/api/registros/ \
  -H "Authorization: Token <tu_token>"
```

### Actualizar un registro
```bash
curl -X PUT http://localhost:8000/api/registros/1/ \
  -H "Authorization: Token <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sitio_id": 1,
    "user_id": 1,
    "registro0": true
  }'
```

### Activar un registro
```bash
curl -X PUT http://localhost:8000/api/registros/1/activar/ \
  -H "Authorization: Token <tu_token>"
```

### Obtener registros activos
```bash
curl -X GET http://localhost:8000/api/registros/activos/ \
  -H "Authorization: Token <tu_token>"
```

### Obtener registros inactivos
```bash
curl -X GET http://localhost:8000/api/registros/inactivos/ \
  -H "Authorization: Token <tu_token>"
```

### Filtrar por sitio usando query params
```bash
curl -X GET "http://localhost:8000/api/registros/por_sitio/?sitio_id=1" \
  -H "Authorization: Token <tu_token>"
```

### Filtrar por sitio usando URL path
```bash
curl -X GET "http://localhost:8000/api/registros/sitio/1/" \
  -H "Authorization: Token <tu_token>"
```

### Usar búsqueda y ordenamiento
```bash
curl -X GET "http://localhost:8000/api/registros/?search=sitio1&ordering=-created_at" \
  -H "Authorization: Token <tu_token>"
```

## Códigos de Respuesta

- `200 OK` - Operación exitosa
- `201 Created` - Recurso creado exitosamente
- `204 No Content` - Recurso eliminado exitosamente
- `400 Bad Request` - Datos inválidos
- `401 Unauthorized` - No autenticado
- `404 Not Found` - Recurso no encontrado

## Ventajas del ViewSet Único

1. **Simplicidad**: Un solo ViewSet maneja todas las operaciones
2. **Consistencia**: Todos los endpoints siguen el mismo patrón
3. **Mantenibilidad**: Código centralizado y fácil de mantener
4. **Escalabilidad**: Fácil agregar nuevos endpoints con @action
5. **Documentación automática**: Mejor integración con herramientas de documentación
6. **Testing unificado**: Un solo lugar para testear toda la funcionalidad

## Notas Importantes

1. Todos los endpoints requieren autenticación
2. El campo `registro0` es un booleano que indica si el registro está activo
3. Los campos `sitio_id` y `user_id` son requeridos para crear/actualizar registros
4. Los campos `id`, `created_at` y `updated_at` son de solo lectura
5. El ViewSet proporciona funcionalidades avanzadas como filtros, búsqueda y ordenamiento
6. Los endpoints personalizados usan el decorador @action de DRF
7. Puedes usar tanto query parameters como URL paths para filtrar por sitio/usuario 