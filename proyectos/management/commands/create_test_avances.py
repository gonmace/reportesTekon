from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models.sites import Site
from proyectos.models import EstructuraProyecto
from reg_visita.models import RegVisita, AvanceProyecto
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea datos de prueba de avances físicos para un sitio'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sitio-id',
            type=int,
            default=1,
            help='ID del sitio para crear avances (default: 1)'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            default=1,
            help='ID del usuario para crear avances (default: 1)'
        )

    def handle(self, *args, **options):
        sitio_id = options['sitio_id']
        user_id = options['user_id']
        
        try:
            sitio = Site.objects.get(id=sitio_id)
            user = User.objects.get(id=user_id)
        except (Site.DoesNotExist, User.DoesNotExist) as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
            return
        
        self.stdout.write(f'🎯 Creando avances de prueba para sitio: {sitio.name}')
        
        # Obtener estructuras de proyecto activas
        estructuras = EstructuraProyecto.objects.filter(activo=True)
        
        if not estructuras.exists():
            self.stdout.write(self.style.ERROR('❌ No hay estructuras de proyecto activas'))
            return
        
        # Crear o obtener registro de visita
        registro, created = RegVisita.objects.get_or_create(
            sitio=sitio,
            user=user,
            defaults={
                'title': f'Reporte de Avance Físico - {sitio.name}',
                'description': 'Reporte de prueba para avances físicos'
            }
        )
        
        if created:
            self.stdout.write(f'✅ Registro de visita creado: {registro.title}')
        else:
            self.stdout.write(f'📋 Usando registro existente: {registro.title}')
        
        # Crear avances para cada estructura
        avances_creados = 0
        
        for estructura in estructuras:
            # Generar valores aleatorios pero realistas
            ejecucion_anterior = Decimal(str(random.randint(0, 60)))
            ejecucion_actual = Decimal(str(random.randint(5, 30)))
            
            # Crear el avance
            avance = AvanceProyecto.objects.create(
                registro=registro,
                proyecto=estructura,
                componente=estructura.componente,
                comentarios=f'Avance de prueba para {estructura.componente.nombre}',
                ejecucion_anterior=ejecucion_anterior,
                ejecucion_actual=ejecucion_actual,
                # ejecucion_acumulada y ejecucion_total se calculan automáticamente en save()
            )
            
            avances_creados += 1
            
            self.stdout.write(f'  ✅ {estructura.componente.nombre}:')
            self.stdout.write(f'    * Ejecución anterior: {float(avance.ejecucion_anterior)}%')
            self.stdout.write(f'    * Ejecución actual: {float(avance.ejecucion_actual)}%')
            self.stdout.write(f'    * Ejecución acumulada: {float(avance.ejecucion_acumulada)}%')
            self.stdout.write(f'    * Ejecución total: {float(avance.ejecucion_total)}%')
        
        # Calcular totales
        total_incidencia = sum(float(e.incidencia) for e in estructuras)
        total_ejecucion = sum(float(a.ejecucion_total) for a in AvanceProyecto.objects.filter(
            is_deleted=False,
            registro__sitio=sitio
        ))
        
        self.stdout.write(f'\n📊 RESUMEN:')
        self.stdout.write(f'  - Avances creados: {avances_creados}')
        self.stdout.write(f'  - Total incidencia: {total_incidencia}%')
        self.stdout.write(f'  - Total ejecución: {total_ejecucion}%')
        
        if total_incidencia > 0:
            porcentaje = (total_ejecucion / total_incidencia * 100)
            self.stdout.write(f'  - Porcentaje de avance: {porcentaje:.1f}%')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Avances de prueba creados exitosamente!'))
        self.stdout.write(f'🔗 Puedes ver los resultados en: /proyectos/sitio/{sitio_id}/avance-fisico/') 