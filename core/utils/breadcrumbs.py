from django.urls import reverse, NoReverseMatch
from django.utils.text import capfirst

class BreadcrumbsMixin:
    def get_page_title(self):
        meta = getattr(self, 'Meta', None)
        if meta and hasattr(meta, 'title'):
            return meta.title

        model = getattr(self, 'model', None)
        if model and hasattr(model._meta, 'verbose_name_plural'):
            return capfirst(model._meta.verbose_name_plural)

        return capfirst(self.__class__.__name__.replace('View', ''))

    def get_header_title(self):
        """Get the header title for the page. Can be overridden in views."""
        meta = getattr(self, 'Meta', None)
        if meta and hasattr(meta, 'header_title'):
            return meta.header_title
        
        # Default to page title if no specific header title is set
        return self.get_page_title()

    def get_breadcrumbs(self):
        meta = getattr(self, 'Meta', None)
        if meta and hasattr(meta, 'breadcrumb'):
            resolved = []
            for item in meta.breadcrumb:
                url = None
                if 'url_name' in item:
                    try:
                        url = reverse(item['url_name'])
                    except NoReverseMatch:
                        url = "#"
                resolved.append({"label": item["label"], "url": url})
            return resolved

        # Auto-generate breadcrumbs based on view name and context
        breadcrumbs = [{"label": "Inicio", "url": reverse("dashboard:dashboard")}]
        
        # Auto-detect parent pages based on view patterns
        if hasattr(self, 'get_parent_breadcrumbs'):
            parent_breadcrumbs = self.get_parent_breadcrumbs()
            breadcrumbs.extend(parent_breadcrumbs)
        else:
            # Try to auto-detect parent based on view name patterns
            parent_breadcrumbs = self._auto_detect_parent_breadcrumbs()
            breadcrumbs.extend(parent_breadcrumbs)
        
        # Add current page
        breadcrumbs.append({"label": self.get_page_title()})
        
        return breadcrumbs
    
    def _auto_detect_parent_breadcrumbs(self):
        """Auto-detect parent breadcrumbs based on view name patterns"""
        view_name = self.__class__.__name__
        
        # Common patterns for parent-child relationships
        parent_patterns = {
            'NuevoRegistroView': {
                'parent_url': 'registro_inicial:list',
                'parent_label': 'Registros Iniciales'
            },
            'EditRegistroView': {
                'parent_url': 'registro_inicial:list',
                'parent_label': 'Registros Iniciales'
            },
            'DetailRegistroView': {
                'parent_url': 'registro_inicial:list',
                'parent_label': 'Registros Iniciales'
            },
            # Add more patterns as needed
        }
        
        if view_name in parent_patterns:
            pattern = parent_patterns[view_name]
            try:
                return [{"label": pattern['parent_label'], "url": reverse(pattern['parent_url'])}]
            except NoReverseMatch:
                return []
        
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.get_page_title()
        context['header_title'] = self.get_header_title()
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context
