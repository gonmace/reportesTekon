from django.core.management.base import BaseCommand
from django.db import transaction
from dashboard.models import DashboardMetric, SitioDashboard
from core.models.sites import Site
from reg_construccion.models import RegConstruccion
from reg_txtss.models import RegTxtss
from users.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

class Command(BaseCommand):
    help = 'Pobla las métricas del dashboard con datos actuales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la actualización de todas las métricas',
        )

    def handle(self, *args, **options):
        self.stdout.write('Iniciando población de métricas del dashboard...')
        
        with transaction.atomic():
            # Actualizar métricas generales
            self.update_general_metrics()
            
            # Actualizar métricas de sitios
            self.update_site_metrics()
            
        self.stdout.write(
            self.style.SUCCESS('Métricas del dashboard actualizadas exitosamente')
        )

    def update_general_metrics(self):
        """Actualiza las métricas generales del dashboard"""
        self.stdout.write('Actualizando métricas generales...')
        
        # Total de sitios
        total_sitios = Site.objects.filter(is_deleted=False).count()
        self.update_metric('sitios_totales', total_sitios)
        
        # Sitios en construcción
        sitios_construccion = RegConstruccion.objects.filter(
            is_deleted=False
        ).values('sitio').distinct().count()
        self.update_metric('sitios_construccion', sitios_construccion)
        
        # Estados de construcción
        estados = RegConstruccion.objects.filter(
            is_deleted=False
        ).values('estado').annotate(
            count=Count('estado')
        )
        
        for estado in estados:
            metric_type = f'sitios_{estado["estado"]}'
            self.update_metric(metric_type, estado['count'])
        
        # Total registros TXTSS
        total_txtss = RegTxtss.objects.filter(is_deleted=False).count()
        self.update_metric('registros_txtss', total_txtss)
        
        # Total registros construcción
        total_construccion = RegConstruccion.objects.filter(is_deleted=False).count()
        self.update_metric('registros_construccion', total_construccion)
        
        # Usuarios activos (último mes)
        ultimo_mes = timezone.now() - timedelta(days=30)
        usuarios_activos = User.objects.filter(
            is_active=True,
            is_deleted=False,
            last_login__gte=ultimo_mes
        ).count()
        self.update_metric('usuarios_activos', usuarios_activos)

    def update_site_metrics(self):
        """Actualiza las métricas específicas de cada sitio"""
        self.stdout.write('Actualizando métricas de sitios...')
        
        sitios = Site.objects.filter(is_deleted=False)
        updated_count = 0
        
        for sitio in sitios:
            sitio_dashboard, created = SitioDashboard.objects.get_or_create(
                sitio=sitio
            )
            sitio_dashboard.update_metrics()
            updated_count += 1
            
            if updated_count % 10 == 0:
                self.stdout.write(f'Procesados {updated_count} sitios...')
        
        self.stdout.write(f'Procesados {updated_count} sitios en total')

    def update_metric(self, metric_type, value):
        """Actualiza una métrica específica"""
        metric, created = DashboardMetric.objects.get_or_create(
            metric_type=metric_type,
            defaults={'value': value}
        )
        
        if not created:
            metric.value = value
            metric.save()
        
        self.stdout.write(f'  - {metric_type}: {value}')
