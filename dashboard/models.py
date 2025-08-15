from django.db import models
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from core.models.sites import Site
from reg_construccion.models import RegConstruccion
from reg_txtss.models import RegTxtss
from users.models import User

class DashboardMetric(models.Model):
    """
    Modelo para almacenar métricas del dashboard que se actualizan periódicamente
    """
    METRIC_TYPES = [
        ('sitios_totales', 'Sitios Totales'),
        ('sitios_construccion', 'Sitios en Construcción'),
        ('sitios_paralizados', 'Sitios Paralizados'),
        ('sitios_concluidos', 'Sitios Concluidos'),
        ('registros_txtss', 'Registros TXTSS'),
        ('registros_construccion', 'Registros Construcción'),
        ('usuarios_activos', 'Usuarios Activos'),
    ]
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES, unique=True)
    value = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Métrica del Dashboard'
        verbose_name_plural = 'Métricas del Dashboard'
    
    def __str__(self):
        return f"{self.get_metric_type_display()}: {self.value}"

class SitioDashboard(models.Model):
    """
    Modelo para almacenar información resumida de sitios para el dashboard
    """
    sitio = models.OneToOneField(Site, on_delete=models.CASCADE, related_name='dashboard_info')
    total_registros_txtss = models.IntegerField(default=0)
    total_registros_construccion = models.IntegerField(default=0)
    ultimo_registro_txtss = models.DateTimeField(null=True, blank=True)
    ultimo_registro_construccion = models.DateTimeField(null=True, blank=True)
    estado_actual = models.CharField(max_length=20, default='sin_estado')
    porcentaje_avance = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Información de Sitio para Dashboard'
        verbose_name_plural = 'Información de Sitios para Dashboard'
    
    def __str__(self):
        return f"Dashboard - {self.sitio.name}"
    
    def update_metrics(self):
        """Actualiza las métricas del sitio"""
        # Contar registros TXTSS
        self.total_registros_txtss = RegTxtss.objects.filter(
            sitio=self.sitio, 
            is_deleted=False
        ).count()
        
        # Contar registros de construcción
        self.total_registros_construccion = RegConstruccion.objects.filter(
            sitio=self.sitio, 
            is_deleted=False
        ).count()
        
        # Último registro TXTSS
        ultimo_txtss = RegTxtss.objects.filter(
            sitio=self.sitio, 
            is_deleted=False
        ).order_by('-created_at').first()
        if ultimo_txtss:
            self.ultimo_registro_txtss = ultimo_txtss.created_at
        
        # Último registro construcción
        ultimo_construccion = RegConstruccion.objects.filter(
            sitio=self.sitio, 
            is_deleted=False
        ).order_by('-created_at').first()
        if ultimo_construccion:
            self.ultimo_registro_construccion = ultimo_construccion.created_at
            self.estado_actual = ultimo_construccion.estado
        
        self.save()

class DashboardStats:
    """
    Clase utilitaria para calcular estadísticas del dashboard
    """
    
    @staticmethod
    def get_sitios_stats():
        """Obtiene estadísticas de sitios"""
        total_sitios = Site.objects.filter(is_deleted=False).count()
        
        # Sitios con registros de construcción
        sitios_con_registros = RegConstruccion.objects.filter(
            is_deleted=False
        ).values('sitio').distinct().count()
        
        # Estados de construcción - contar sitios únicos por estado
        from django.db.models import Max, Subquery, OuterRef
        
        # Obtener sitios que tienen registros de construcción
        sitios_con_construccion = Site.objects.filter(
            is_deleted=False,
            reg_construccion__is_deleted=False
        ).distinct()
        
        # Contar sitios por estado usando el estado más reciente de cada sitio
        estados_dict = {}
        for sitio in sitios_con_construccion:
            # Obtener el estado del registro más reciente de este sitio
            ultimo_registro = sitio.reg_construccion.filter(
                is_deleted=False
            ).order_by('-created_at').first()
            
            if ultimo_registro:
                estado = ultimo_registro.estado
                estados_dict[estado] = estados_dict.get(estado, 0) + 1
        
        return {
            'total_sitios': total_sitios,
            'sitios_con_registros': sitios_con_registros,
            'estados': estados_dict,
        }
    
    @staticmethod
    def get_registros_stats():
        """Obtiene estadísticas de registros"""
        total_txtss = RegTxtss.objects.filter(is_deleted=False).count()
        total_construccion = RegConstruccion.objects.filter(is_deleted=False).count()
        
        # Registros del último mes
        ultimo_mes = timezone.now() - timedelta(days=30)
        txtss_ultimo_mes = RegTxtss.objects.filter(
            created_at__gte=ultimo_mes,
            is_deleted=False
        ).count()
        
        construccion_ultimo_mes = RegConstruccion.objects.filter(
            created_at__gte=ultimo_mes,
            is_deleted=False
        ).count()
        
        return {
            'total_txtss': total_txtss,
            'total_construccion': total_construccion,
            'txtss_ultimo_mes': txtss_ultimo_mes,
            'construccion_ultimo_mes': construccion_ultimo_mes,
        }
    
    @staticmethod
    def get_usuarios_stats():
        """Obtiene estadísticas de usuarios"""
        total_usuarios = User.objects.filter(is_active=True, is_deleted=False).count()
        
        # Usuarios activos en el último mes
        ultimo_mes = timezone.now() - timedelta(days=30)
        usuarios_activos = User.objects.filter(
            is_active=True,
            is_deleted=False,
            last_login__gte=ultimo_mes
        ).count()
        
        return {
            'total_usuarios': total_usuarios,
            'usuarios_activos': usuarios_activos,
        }
    
    @staticmethod
    def get_sitios_detallados():
        """Obtiene información detallada de sitios para el dashboard"""
        sitios = Site.objects.filter(is_deleted=False).prefetch_related(
            'reg_txtss',
            'reg_construccion'
        )
        
        sitios_data = []
        for sitio in sitios:
            # Último registro de construcción
            ultimo_construccion = sitio.reg_construccion.filter(
                is_deleted=False
            ).order_by('-created_at').first()
            
            # Último registro TXTSS
            ultimo_txtss = sitio.reg_txtss.filter(
                is_deleted=False
            ).order_by('-created_at').first()
            
            # Contar registros
            total_txtss = sitio.reg_txtss.filter(is_deleted=False).count()
            total_construccion = sitio.reg_construccion.filter(is_deleted=False).count()
            
            sitios_data.append({
                'sitio': sitio,
                'estado': ultimo_construccion.estado if ultimo_construccion else 'sin_estado',
                'ultimo_registro_txtss': ultimo_txtss.created_at if ultimo_txtss else None,
                'ultimo_registro_construccion': ultimo_construccion.created_at if ultimo_construccion else None,
                'total_txtss': total_txtss,
                'total_construccion': total_construccion,
            })
        
        return sitios_data
