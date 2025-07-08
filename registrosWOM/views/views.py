from django.views.generic import TemplateView, CreateView, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from core.utils.breadcrumbs import BreadcrumbsMixin
from core.models.sites import Site
from ..serializers import SiteWithRegistrosSerializer


class ListRegistrosView(LoginRequiredMixin, BreadcrumbsMixin, TemplateView):
    template_name = 'pages/list.html'
    context_object_name = 'registros'

    class Meta:
        title = 'Registros'
        header_title = 'Registros WOM'

class RegistrosViewSet(viewsets.ModelViewSet):
    serializer_class = SiteWithRegistrosSerializer  
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Site.objects.filter(user__isnull=False)
    
# class CreateRegistro0View(LoginRequiredMixin, BreadcrumbsMixin, CreateView):
#     model = Registros
#     form_class = RegistroInicialForm
#     template_name = 'pages/create.html'
#     success_url = reverse_lazy('registrosWOM:list')
    
#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         return super().form_valid(form)