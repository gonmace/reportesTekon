# Template de Mapa Extraído

## 📍 **Descripción**

El template `components/mapa.html` ha sido extraído de `step_generic.html` (línea 93) para permitir su reutilización y personalización en configuraciones de mapa.

## 🎯 **Características**

### ✅ **Funcionalidades Incluidas**
- Modal responsivo para mostrar mapas
- Soporte para múltiples puntos (hasta 3 coordenadas)
- Leyenda dinámica generada automáticamente
- Carga dinámica de Leaflet.js
- Marcadores personalizables con colores y tamaños
- Líneas de conexión entre puntos
- Función de guardado de imagen del mapa
- Controles de zoom y escala
- Cálculo automático de zoom óptimo

### 🎨 **Personalización de Marcadores**
- **Colores**: Personalizables por punto
- **Tamaños**: `tiny`, `small`, `normal`, `mid`, `large`, `xlarge`
- **Tipos**: `marker`, `circle`, etc.

## 🔧 **Uso en Configuraciones**

### **Configuración Básica**
```python
from registros.config import create_multi_point_map_config

sitio_mapa_component = create_multi_point_map_config(
    model_class1='current',
    lat1='lat',
    lon1='lon', 
    name1='Inspección',
    icon1_color='red',
    icon1_size='large',
    icon1_type='marker',
    model_class2=Site,
    lat2='lat_base',
    lon2='lon_base', 
    name2='Mandato',
    second_model_relation_field='sitio',
    descripcion_distancia='Desfase Mandato-Inspección',
    icon2_color='blue',
    icon2_size='normal',
    icon2_type='marker',
    zoom=15,
    template_name='components/mapa.html',  # Template extraído
)
```

### **Configuración de Punto Único**
```python
from registros.config import create_single_point_map_config

mapa_component = create_single_point_map_config(
    lat_field='latitud',
    lon_field='longitud',
    name_field='nombre',
    zoom=15,
    template_name='components/mapa.html',  # Template extraído
    icon_color='green',
    icon_size='large',
    icon_type='marker'
)
```

## 📁 **Estructura del Template**

```
templates/
└── components/
    └── mapa.html  # ← Template extraído
```

### **Componentes del Template**
1. **Modal HTML**: Estructura del modal con header, leyenda y contenedor del mapa
2. **CSS de Leaflet**: Carga automática de estilos
3. **JavaScript de Leaflet**: Carga dinámica de la librería
4. **Funciones JavaScript**:
   - `openMapModal()`: Abre el modal y procesa coordenadas
   - `closeMapModal()`: Cierra el modal y limpia recursos
   - `initMap()`: Inicializa el mapa
   - `loadLeaflet()`: Carga Leaflet dinámicamente
   - `createMap()`: Crea y configura el mapa
   - `saveMapImage()`: Guarda imagen del mapa

## 🎛️ **Personalización**

### **Modificar Colores de Marcadores**
```python
sitio_mapa_component = create_multi_point_map_config(
    # ... otros parámetros ...
    icon1_color='#FF6B6B',  # Color personalizado
    icon2_color='#4ECDC4',  # Color personalizado
)
```

### **Modificar Tamaños de Marcadores**
```python
sitio_mapa_component = create_multi_point_map_config(
    # ... otros parámetros ...
    icon1_size='xlarge',  # Marcador extra grande
    icon2_size='small',   # Marcador pequeño
)
```

### **Modificar Zoom**
```python
sitio_mapa_component = create_multi_point_map_config(
    # ... otros parámetros ...
    zoom=18,  # Zoom más cercano
)
```

## 🔄 **Integración con el Sistema**

### **En Configuraciones de Pasos**
```python
PASOS_CONFIG = {
    'sitio': create_custom_config(
        model_class=RSitio,
        form_class=RSitioForm,
        title='Sitio',
        description='Información general del sitio.',
        template_form='components/elemento_form.html',
        sub_elementos=[sitio_mapa_component]  # ← Componente de mapa
    ),
}
```

### **En Configuraciones de Registro**
```python
REGISTRO_CONFIG = create_registro_config(
    registro_model=RegTxtss,
    pasos_config=PASOS_CONFIG,
    title='TX/TSS',
    app_namespace='reg_txtss',
    list_template='pages/main_txtss.html',
    steps_template='pages/steps_txtss.html'
)
```

## 🚀 **Ventajas del Template Extraído**

1. **Reutilización**: Un solo template para todos los mapas
2. **Mantenimiento**: Cambios centralizados en un archivo
3. **Personalización**: Fácil modificación de estilos y funcionalidad
4. **Consistencia**: Mismo comportamiento en toda la aplicación
5. **Modularidad**: Separación clara de responsabilidades

## 📝 **Notas de Implementación**

- El template incluye toda la funcionalidad JavaScript necesaria
- La carga de Leaflet es dinámica para optimizar el rendimiento
- El modal se incluye una sola vez por página (controlado por `{% if forloop.first %}`)
- Los botones de mapa deben tener el atributo `data-*` correcto para funcionar
- El template es compatible con el sistema de breadcrumbs existente

## 🔧 **Troubleshooting**

### **Problema**: El mapa no se muestra
**Solución**: Verificar que los botones tengan los atributos `data-*` correctos

### **Problema**: Leaflet no se carga
**Solución**: Verificar que los archivos estáticos estén disponibles

### **Problema**: El modal no se abre
**Solución**: Verificar que el JavaScript se ejecute después del DOM

## 📚 **Referencias**

- **Template original**: `templates/components/step_generic.html` (línea 93)
- **Configuración**: `registros/config.py`
- **Ejemplo de uso**: `reg_txtss/config.py` 