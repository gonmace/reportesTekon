from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.utils.breadcrumbs import BreadcrumbsMixin


class ListRegistrosView(LoginRequiredMixin, BreadcrumbsMixin, TemplateView):
    template_name = 'pages/list.html'
    context_object_name = 'registros'

    class Meta:
        title = 'Registros Tx/Tss'
        header_title = 'Registros Tx/Tss'

    