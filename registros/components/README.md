# Arquitectura de Elementos Genéricos

Esta nueva arquitectura proporciona una forma unificada y reutilizable de manejar formularios, sub-elementos (fotos, mapas, tablas, etc.) y la lógica de negocio asociada.

## Componentes Principales

### 1. ElementoRegistro (Base)
Clase base que proporciona la funcionalidad común para todos los elementos:
- Gestión de formularios
- Manejo de instancias de modelos
- Sub-elementos configurables
- Validación y guardado
- Información de completitud

### 2. SubElemento (Base)
Clase base para sub-elementos como fotos, mapas, tablas, etc.:
- Renderizado de templates
- Obtención de datos específicos
- Integración con elementos padre

### 3. Vistas Genéricas
- `ElementoView`: Maneja peticiones AJAX
- `ElementoFormView`: Renderiza formularios
- `StepsRegistroElementosView`: Vista de pasos usando elementos

## Implementación en registros_txtss

### Elementos Específicos
```python
# registros_txtss/elementos.py
class ElementoSitio(ElementoRegistro):
    model = RSitio
    form_class = RSitioForm
    tipo = 'sitio'
    sub_elementos = {
        'map': 'SubElementoMap',
        'photos': 'SubElementoPhotos',
        'table': 'SubElementoTable',
    }
```

### URLs
```python
# Rutas de elementos
path("registros/<int:registro_id>/elemento/<str:tipo_elemento>/", ElementoView.as_view(), name="elemento"),
path("registros/<int:registro_id>/elemento/<str:tipo_elemento>/form/", ElementoFormView.as_view(), name="elemento_form"),
path("registros/<int:registro_id>/elementos/", StepsRegistroElementosView.as_view(), name="steps_elementos"),
```

## Uso

### 1. Crear un Elemento
```python
from registros_txtss.elementos import ElementoSitio

registro = Registros.objects.get(id=1)
elemento = ElementoSitio(registro)
```

### 2. Obtener Formulario
```python
form = elemento.get_form()
```

### 3. Obtener Sub-elementos
```python
sub_elementos = elemento.get_all_sub_elementos()
mapa = elemento.get_sub_elemento('map')
fotos = elemento.get_sub_elemento('photos')
```

### 4. Guardar Datos
```python
if form.is_valid():
    elemento.save(form)
```

### 5. Información de Completitud
```python
completeness_info = elemento.get_completeness_info()
```

## Ventajas

1. **Reutilización**: Una sola implementación para múltiples tipos de elementos
2. **Consistencia**: Interfaz unificada para todos los elementos
3. **Extensibilidad**: Fácil agregar nuevos tipos de sub-elementos
4. **Mantenibilidad**: Lógica centralizada y bien organizada
5. **Flexibilidad**: Configuración por elemento y sub-elemento

## Migración

### Antes (Vista Tradicional)
```python
class RSitioView(GenericRegistroView):
    form_class = RSitioForm
    
    def setup(self, request, *args, **kwargs):
        kwargs['model_class'] = RSitio
        kwargs['etapa'] = 'sitio'
        super().setup(request, *args, **kwargs)
```

### Después (Elemento)
```python
# URLs
path("registros/<int:registro_id>/elemento/sitio/", ElementoView.as_view(), name="elemento_sitio"),

# Uso
elemento = ElementoSitio(registro)
form = elemento.get_form()
sub_elementos = elemento.get_all_sub_elementos()
```

## Próximos Pasos

1. **Migrar vistas existentes**: Reemplazar las vistas tradicionales con elementos
2. **Agregar más sub-elementos**: Implementar gráficos, documentos, etc.
3. **Mejorar templates**: Crear templates específicos para cada tipo de elemento
4. **Testing**: Agregar tests unitarios para los elementos
5. **Documentación**: Expandir la documentación con ejemplos prácticos

## URLs de Prueba

- Vista de pasos con elementos: `/txtss/registros/1/elementos/`
- Formulario de sitio: `/txtss/registros/1/elemento/sitio/form/`
- API de sitio: `/txtss/registros/1/elemento/sitio/` 