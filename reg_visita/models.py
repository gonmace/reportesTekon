"""
Modelos para registros Reporte de visita.
"""

from registros.models.base import RegistroBase
from registros.models.paso import PasoBase
from django.db import models
from registros.models.validators import validar_latitud, validar_longitud
from registros.models.completeness_checker import check_model_completeness
from core.models.sites import Site
from users.models import User
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal

class RegVisita(RegistroBase):
    """
    Modelo para registros Reporte de visita.
    """
    sitio = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Sitio")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    title = models.CharField(max_length=100, verbose_name='Título')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"RegVisita {self.id}"
    
    def clean(self):
        """Custom validation method"""
        super().clean()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def create_default_avance_proyecto(self):
        """
        Crea automáticamente un registro de AvanceProyecto para este registro de visita.
        Busca el último avance del sitio y copia la ejecución acumulada como ejecución anterior.
        """
        try:
            from proyectos.models import EstructuraProyecto, Componente
            
            # Obtener todas las estructuras de proyecto activas
            estructuras_proyecto = EstructuraProyecto.objects.filter(activo=True)
            
            if not estructuras_proyecto.exists():
                # Si no hay estructuras de proyecto, crear uno sin proyecto
                avance = AvanceProyecto.objects.create(
                    registro=self,
                    proyecto=None,
                    componente=None,
                    comentarios=f'Avance automático creado para {self.title} (sin proyecto asignado)',
                    ejecucion_anterior=Decimal('0.00'),
                    ejecucion_actual=Decimal('0.00'),
                    ejecucion_acumulada=Decimal('0.00'),
                    ejecucion_total=Decimal('0.00')
                )
                return avance
            
            # Crear avances para todas las estructuras de proyecto
            avances_creados = []
            for estructura in estructuras_proyecto:
                # Buscar el último avance para esta estructura en este sitio
                ultimo_avance = AvanceProyecto.objects.filter(
                    is_deleted=False,
                    registro__sitio=self.sitio,
                    proyecto=estructura
                ).exclude(registro=self).order_by('-created_at').first()
                
                if ultimo_avance:
                    # Copiar la ejecución acumulada del último avance como ejecución anterior
                    ejecucion_anterior = ultimo_avance.ejecucion_acumulada
                    ejecucion_actual = Decimal('0.00')
                else:
                    # Si no hay avance previo, empezar desde 0
                    ejecucion_anterior = Decimal('0.00')
                    ejecucion_actual = Decimal('0.00')
                
                # Crear el registro de avance de proyecto
                avance = AvanceProyecto.objects.create(
                    registro=self,
                    proyecto=estructura,
                    componente=estructura.componente,
                    comentarios=f'Avance automático creado para {self.title} - {estructura.componente.nombre}',
                    ejecucion_anterior=ejecucion_anterior,
                    ejecucion_actual=ejecucion_actual,
                    ejecucion_acumulada=max(ejecucion_anterior, ejecucion_actual),
                    ejecucion_total=(max(ejecucion_anterior, ejecucion_actual) * estructura.incidencia) / 100
                )
                avances_creados.append(avance)
            
            return avances_creados[0] if avances_creados else None
                
        except Exception as e:
            # Log del error pero no fallar la creación del registro
            print(f"Error al crear avance de proyecto automático: {e}")
            return None


class AvanceProyecto(PasoBase):
    """Paso Visita para registros Reporte de visita."""
    registro = models.ForeignKey(RegVisita, on_delete=models.CASCADE, verbose_name='Registro')
    proyecto = models.ForeignKey(
        'proyectos.EstructuraProyecto', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='Estructura Proyecto',
        help_text='Seleccione la estructura de proyecto relacionado con esta visita'
    )
    componente = models.ForeignKey(
        'proyectos.Componente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Componente',
        help_text='Componente específico del proyecto'
    )
    comentarios = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='Comentarios',
        help_text='Comentarios adicionales sobre el avance del proyecto'
    )
    ejecucion_anterior = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=Decimal('0.00'),
        verbose_name='% Ejecución Anterior',
        help_text='Porcentaje de ejecución del período anterior'
    )
    ejecucion_actual = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=Decimal('0.00'),
        verbose_name='% Ejecución Actual',
        help_text='Porcentaje de ejecución del período actual'
    )
    ejecucion_acumulada = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        default=Decimal('0.00'),
        verbose_name='% Ejecución Acumulada',
        help_text='Porcentaje de ejecución acumulada total'
    )
    ejecucion_total = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        default=Decimal('0.00'),
        verbose_name='% Ejecución Total',
        help_text='Porcentaje de ejecución total ponderado'
    )

    class Meta:
        verbose_name = 'Avance de Proyecto'
        verbose_name_plural = 'Avances de Proyecto'
        ordering = ['-created_at']

    def __str__(self):
        return f"Avance {self.id} - {self.registro.title}"

    def save(self, *args, **kwargs):
        """Calcula automáticamente la ejecución acumulada y total"""
        # La ejecución acumulada es la suma de anterior + actual
        self.ejecucion_acumulada = self.ejecucion_anterior + self.ejecucion_actual
        
        # La ejecución total es la incidencia * ejecución acumulada / 100
        if self.proyecto and self.proyecto.incidencia:
            self.ejecucion_total = (self.proyecto.incidencia * self.ejecucion_acumulada) / Decimal('100')
        else:
            self.ejecucion_total = self.ejecucion_acumulada
        
        super().save(*args, **kwargs)


# Signal para crear automáticamente un AvanceProyecto cuando se crea un RegVisita
@receiver(post_save, sender=RegVisita)
def create_avance_proyecto_on_registro_creation(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta cuando se crea un nuevo RegVisita.
    Crea automáticamente registros de AvanceProyecto para todas las estructuras activas.
    """
    if created:
        # Solo crear si no existe ya un avance para este registro
        if not AvanceProyecto.objects.filter(registro=instance).exists():
            instance.create_default_avance_proyecto()

