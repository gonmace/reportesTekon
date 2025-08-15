from django.views.generic import TemplateView
from core.utils.breadcrumbs import BreadcrumbsMixin
from dashboard.models import DashboardStats
from reg_construccion.models import RegConstruccion
from datetime import datetime


class DashboardView(BreadcrumbsMixin, TemplateView):
    template_name = 'pages/dashboard.html'
    
    class Meta:
        title = 'Dashboard'
        header_title = 'Dashboard'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener estadísticas generales
        sitios_stats = DashboardStats.get_sitios_stats()
        registros_stats = DashboardStats.get_registros_stats()
        usuarios_stats = DashboardStats.get_usuarios_stats()
        
        # Preparar datos para el gráfico
        estados_chart_data = []
        for value, label in RegConstruccion.ESTADO_CHOICES:
            count = sitios_stats['estados'].get(value, 0)
            estados_chart_data.append(count)
        
        # Obtener fecha actual y número de semana
        fecha_actual = datetime.now()
        numero_semana = fecha_actual.isocalendar()[1]
        
        context.update({
            'sitios_stats': sitios_stats,
            'registros_stats': registros_stats,
            'usuarios_stats': usuarios_stats,
            'estados_choices': RegConstruccion.ESTADO_CHOICES,
            'estados_chart_data': estados_chart_data,
            'fecha_actual': fecha_actual,
            'numero_semana': numero_semana,
        })
        
        return context