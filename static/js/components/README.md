# Componentes JavaScript Reutilizables

## Alertas (alerts.js)

Componente reutilizable para mostrar alertas usando DaisyUI que puede ser usado en todas las apps del proyecto.

### Inclusión del Componente

Para usar el componente de alertas, incluye el archivo en tu template:

```html
<script src="{% static 'js/components/alerts.js' %}"></script>
```

### Uso Básico

```javascript
// Mostrar alerta de éxito
Alert.success('Operación completada exitosamente');

// Mostrar alerta de error
Alert.error('Ha ocurrido un error');

// Mostrar alerta de advertencia
Alert.warning('Ten cuidado con esta acción');

// Mostrar alerta informativa
Alert.info('Información importante');
```

### Métodos Disponibles

#### `Alert.show(message, type, options)`
Muestra una alerta con opciones personalizadas.

**Parámetros:**
- `message` (string): Mensaje a mostrar
- `type` (string): Tipo de alerta ('success', 'error', 'warning', 'info')
- `options` (object): Opciones adicionales
  - `autoHide` (number): Tiempo en ms para auto-ocultar (0 = no auto-ocultar)
  - `id` (string): ID personalizado para la alerta
  - `dismissible` (boolean): Si la alerta se puede cerrar
  - `icon` (string): Clase del icono (FontAwesome)

**Ejemplo:**
```javascript
Alert.show('Mensaje personalizado', 'success', {
    autoHide: 5000,
    dismissible: true,
    icon: 'fa-solid fa-star'
});
```

#### `Alert.success(message, options)`
Muestra una alerta de éxito.

#### `Alert.error(message, options)`
Muestra una alerta de error.

#### `Alert.warning(message, options)`
Muestra una alerta de advertencia.

#### `Alert.info(message, options)`
Muestra una alerta informativa.

#### `Alert.confirm(message, onConfirm, onCancel, options)`
Muestra una alerta de confirmación con botones Sí/No.

**Ejemplo:**
```javascript
Alert.confirm(
    '¿Estás seguro de que quieres eliminar este elemento?',
    () => {
        // Código a ejecutar si se confirma
        console.log('Confirmado');
    },
    () => {
        // Código a ejecutar si se cancela
        console.log('Cancelado');
    }
);
```

#### `Alert.hide(id)`
Oculta una alerta específica por su ID.

#### `Alert.hideAll()`
Oculta todas las alertas activas.

### Ejemplos de Uso en Diferentes Contextos

#### 1. Después de una operación AJAX exitosa:
```javascript
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        Alert.success('Datos guardados correctamente', { autoHide: 3000 });
    } else {
        Alert.error(data.message || 'Error al guardar los datos');
    }
})
.catch(error => {
    Alert.error('Error de conexión');
});
```

#### 2. Validación de formularios:
```javascript
function validateForm() {
    const email = document.getElementById('email').value;
    
    if (!email) {
        Alert.error('El campo email es requerido');
        return false;
    }
    
    if (!email.includes('@')) {
        Alert.warning('Por favor ingresa un email válido');
        return false;
    }
    
    return true;
}
```

#### 3. Confirmación antes de eliminar:
```javascript
function deleteItem(itemId, itemName) {
    Alert.confirm(
        `¿Estás seguro de que quieres eliminar "${itemName}"?`,
        () => {
            // Proceder con la eliminación
            performDelete(itemId);
        },
        () => {
            // Cancelar eliminación
            console.log('Eliminación cancelada');
        }
    );
}
```

### Personalización

El componente usa las clases de DaisyUI para los estilos. Puedes personalizar los colores y estilos modificando las clases CSS en tu tema de DaisyUI.

### Posicionamiento

Las alertas aparecen en la esquina superior derecha de la pantalla. Si necesitas cambiar la posición, modifica las clases CSS en el método `init()` del componente:

```javascript
this.alertContainer.className = 'fixed top-4 right-4 z-50 space-y-2 max-w-sm';
```

### Compatibilidad

- Requiere DaisyUI
- Requiere FontAwesome para los iconos
- Compatible con todos los navegadores modernos
- No requiere dependencias adicionales 