from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView, DeleteView
from core.models.sites import Site
from django.contrib.auth.mixins import LoginRequiredMixin
from django_tables2 import SingleTableView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from core.utils.breadcrumbs import BreadcrumbsMixin
from django.http import JsonResponse
from django.core.serializers import serialize
import json

# views.py
class SitiosView(LoginRequiredMixin, BreadcrumbsMixin, TemplateView):
    template_name = 'pages/sitios.html'
    context_object_name = 'sitios'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_superuser'] = self.request.user.is_superuser
        return context

class SitiosAPIView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        sites = Site.objects.all()
        
        # Serializar los datos
        data = []
        for site in sites:
            site_data = {
                'id': site.id,
                'operator_id': site.operator_id or '',
                'pti_cell_id': site.pti_cell_id or '',
                'name': site.name,
                'region': site.region or '',
                'comuna': site.comuna or '',
                'lat_base': site.lat_base,
                'lon_base': site.lon_base,
                'alt': site.alt or '',
            }
            data.append(site_data)
        
        return JsonResponse({'data': data})


class SiteEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Site
    fields = ['pti_cell_id', 'operator_id', 'name', 'lat_base', 'lon_base', 'alt', 'region', 'comuna']
    template_name = 'sites/site_form.html'
    success_url = reverse_lazy('sitios')

    def test_func(self):
        return self.request.user.is_superuser  # Solo superusuarios pueden editar

class SiteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Site
    template_name = 'sites/site_confirm_delete.html'
    success_url = reverse_lazy('sitios')

    def test_func(self):
        return self.request.user.is_superuser  # Solo superusuarios pueden eliminar
