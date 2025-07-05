# Solución al Flash Blanco en Dark Mode

## Problema
Al cambiar de Dashboard a Sitios (o cualquier otra página) en dark mode, ocurría un flash blanco momentáneo antes de que se aplicara el tema oscuro.

## Causa del Problema
El flash ocurría porque:
1. El HTML se renderizaba con `data-theme="light"` por defecto
2. El JavaScript que aplica el tema se ejecutaba después de `DOMContentLoaded`
3. Entre la carga inicial y la aplicación del tema, se mostraba brevemente el tema claro

## Solución Implementada

### 1. Script Inline en `<head>` (base.html)
```html
<script>
    // Aplicar el tema inmediatamente para evitar flash
    (function() {
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const theme = savedTheme || (prefersDark ? 'dark' : 'light');
        document.documentElement.setAttribute('data-theme', theme);
    })();
</script>
```

### 2. CSS para Transiciones Suaves (theme-transitions.css)
```css
/* Transiciones suaves para cambios de tema */
* {
    transition: background-color 0.2s ease-in-out, 
                color 0.2s ease-in-out, 
                border-color 0.2s ease-in-out;
}

/* Evitar transiciones durante la carga inicial */
html[data-theme] * {
    transition: none;
}

/* Aplicar transiciones solo después de la carga completa */
html.theme-loaded * {
    transition: background-color 0.2s ease-in-out, 
                color 0.2s ease-in-out, 
                border-color 0.2s ease-in-out;
}
```

### 3. Script de Navegación (theme-navigation.js)
- Maneja la navegación entre páginas
- Aplica el tema antes de que se cargue la nueva página
- Maneja el cache del navegador

### 4. Optimización del Script del Header
- Simplificado para usar el tema ya aplicado
- Agrega la clase `theme-loaded` después de la carga

## Archivos Modificados

1. **templates/base.html**
   - Removido `data-theme="light"` hardcodeado
   - Agregado script inline para aplicar tema inmediatamente
   - Incluido script de navegación

2. **templates/components/common/header.html**
   - Simplificado el script de tema
   - Agregada clase `theme-loaded` para transiciones

3. **templates/base_head.html**
   - Incluido CSS de transiciones

4. **static/css/theme-transitions.css** (nuevo)
   - Manejo de transiciones suaves

5. **static/js/theme-navigation.js** (nuevo)
   - Manejo de navegación entre páginas

## Beneficios

✅ **Elimina el flash blanco** al cargar páginas en dark mode
✅ **Transiciones suaves** entre temas
✅ **Mejor experiencia de usuario** en navegación
✅ **Compatibilidad** con cache del navegador
✅ **Respeto** por las preferencias del sistema

## Cómo Funciona

1. **Carga Inicial**: El script inline aplica el tema antes de que se renderice cualquier contenido
2. **Navegación**: El script de navegación asegura que el tema se mantenga entre páginas
3. **Transiciones**: El CSS maneja las transiciones de manera suave después de la carga completa
4. **Cache**: Se maneja correctamente cuando las páginas se cargan desde el cache

## Testing

Para verificar que funciona:
1. Activa dark mode
2. Navega entre Dashboard y Sitios
3. Usa los botones atrás/adelante del navegador
4. Recarga la página (Ctrl+F5)

No debería haber flash blanco en ninguno de estos casos. 