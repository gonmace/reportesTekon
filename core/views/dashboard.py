from django.views.generic import TemplateView
from core.utils.breadcrumbs import BreadcrumbsMixin


class DashboardView(BreadcrumbsMixin, TemplateView):
    template_name = 'pages/dashboard.html'
    
    class Meta:
        title = 'Dashboard'
        header_title = 'Dashboard'