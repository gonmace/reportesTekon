# Sistema de Header Title

Este documento explica cómo capturar y mostrar el `header_title` de cada página en tu aplicación Django.

## Cómo funciona

El sistema utiliza el `BreadcrumbsMixin` que ya tienes implementado, pero ahora también maneja el `header_title` que se muestra en el header de la aplicación.

## Implementación

### 1. En las vistas (views.py)

Para que una vista pase el `header_title` al template, debes:

1. **Heredar de `BreadcrumbsMixin`**
2. **Definir una clase `Meta` con `header_title`**

```python
from django.views.generic import TemplateView
from core.utils.breadcrumbs import BreadcrumbsMixin

class MiVistaView(BreadcrumbsMixin, TemplateView):
    template_name = 'pages/mi_pagina.html'
    
    class Meta:
        title = 'Mi Página'  # Para breadcrumbs
        header_title = 'Gestión de Mi Página'  # Para el header
```

### 2. En el template (header.html)

El header ya está configurado para mostrar el `header_title`:

```html
<h2 class="text-xl font-semibold text-primary hidden md:block">
    {{ header_title|default:"Dashboard" }}
</h2>
```

## Ejemplos de uso

### Ejemplo 1: Vista simple
```python
class DashboardView(BreadcrumbsMixin, TemplateView):
    template_name = 'pages/dashboard.html'
    
    class Meta:
        title = 'Dashboard'
        header_title = 'Panel Principal'
```

### Ejemplo 2: Vista con lógica personalizada
```python
class SitiosView(LoginRequiredMixin, BreadcrumbsMixin, TemplateView):
    template_name = 'pages/sitios.html'
    
    class Meta:
        title = 'Sitios'
        header_title = 'Gestión de Sitios'
    
    def get_header_title(self):
        # Puedes personalizar el header_title dinámicamente
        if self.request.user.is_superuser:
            return 'Administración de Sitios'
        return 'Gestión de Sitios'
```

### Ejemplo 3: Vista basada en modelo
```python
class SiteDetailView(LoginRequiredMixin, BreadcrumbsMixin, DetailView):
    model = Site
    template_name = 'sites/site_detail.html'
    
    class Meta:
        title = 'Detalle de Sitio'
        header_title = 'Información del Sitio'
    
    def get_header_title(self):
        # Usar el nombre del sitio en el header
        site = self.get_object()
        return f'Sitio: {site.name}'
```

## Variables disponibles en el contexto

Cuando usas `BreadcrumbsMixin`, tienes acceso a estas variables en tus templates:

- `header_title`: El título que aparece en el header
- `page_title`: El título de la página (para breadcrumbs)
- `breadcrumbs`: Array de breadcrumbs para navegación

## Fallback

Si no defines `header_title` en la clase `Meta`, el sistema usará automáticamente el `page_title` como `header_title`.

## Migración de vistas existentes

Para migrar vistas existentes:

1. Agrega `BreadcrumbsMixin` a la herencia
2. Define la clase `Meta` con `title` y `header_title`
3. El resto de tu código permanece igual

```python
# Antes
class MiVistaView(TemplateView):
    template_name = 'pages/mi_pagina.html'

# Después
class MiVistaView(BreadcrumbsMixin, TemplateView):
    template_name = 'pages/mi_pagina.html'
    
    class Meta:
        title = 'Mi Página'
        header_title = 'Gestión de Mi Página'
``` 