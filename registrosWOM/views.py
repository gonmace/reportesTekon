from django.views.generic import TemplateView, CreateView, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from core.utils.breadcrumbs import BreadcrumbsMixin
from core.serializers import SiteSerializer
from core.models.sites import Site
from .serializers import SiteWithRegistroInicialSerializer

class ListRegistrosView(LoginRequiredMixin, BreadcrumbsMixin, TemplateView):
    template_name = 'pages/list.html'
    context_object_name = 'registros'

    class Meta:
        title = 'Registros WOM'
        header_title = 'Registros WOM'

class RegistrosViewSet(viewsets.ModelViewSet):
    serializer_class = SiteWithRegistroInicialSerializer
    permission_classes = [AllowAny]  # Temporalmente para desarrollo
    
    def get_queryset(self):
        return Site.objects.filter(user__isnull=False)