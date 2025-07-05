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

        return [
            {"label": "Inicio", "url": reverse("dashboard:dashboard")},
            {"label": self.get_page_title()},
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.get_page_title()
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context
