from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.utils.breadcrumbs import BreadcrumbsMixin
from ..forms.activar import ActivarRegistroForm


class ListRegistrosView(LoginRequiredMixin, BreadcrumbsMixin, TemplateView):
    template_name = 'pages/main_txtss.html'
    context_object_name = 'registros'

    class Meta:
        title = 'Registros Tx/Tss'
        header_title = 'Registros Tx/Tss'
        breadcrumbs = [
            {'label': 'Inicio', 'url_name': 'dashboard:dashboard'},
            {'label': 'TX/TSS'}
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ActivarRegistroForm()
        return context

    