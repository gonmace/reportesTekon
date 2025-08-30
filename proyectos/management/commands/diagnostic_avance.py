from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models.sites import Site
from proyectos.models import EstructuraProyecto, Grupo, Componente
from reg_visita.models import AvanceProyecto, RegVisita
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Diagnóstico para verificar por qué la suma de ejecución total da cero'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sitio-id',
            type=int,
            help='ID del sitio a diagnosticar'
        )

    def handle(self, *args, **options):
        sitio_id = options.get('sitio_id')
        
        self.stdout.write('🔍 DIAGNÓSTICO DE AVANCE FÍSICO')
        self.stdout.write('=' * 50)
        
        # Verificar sitios
        sitios = Site.objects.all()
        self.stdout.write(f'\n📋 SITIOS DISPONIBLES ({sitios.count()}):')
        for sitio in sitios:
            self.stdout.write(f'  - ID: {sitio.id}, Nombre: {sitio.name}')
        
        if sitio_id:
            sitio = Site.objects.filter(id=sitio_id).first()
            if not sitio:
                self.stdout.write(self.style.ERROR(f'❌ Sitio con ID {sitio_id} no encontrado'))
                return
        else:
            sitio = sitios.first()
            if not sitio:
                self.stdout.write(self.style.ERROR('❌ No hay sitios en la base de datos'))
                return
        
        self.stdout.write(f'\n🎯 DIAGNOSTICANDO SITIO: {sitio.name} (ID: {sitio.id})')
        
        # Verificar grupos
        grupos = Grupo.objects.filter(activo=True)
        self.stdout.write(f'\n📊 GRUPOS ACTIVOS ({grupos.count()}):')
        for grupo in grupos:
            self.stdout.write(f'  - {grupo.nombre}')
        
        # Verificar componentes
        componentes = Componente.objects.filter(activo=True)
        self.stdout.write(f'\n🔧 COMPONENTES ACTIVOS ({componentes.count()}):')
        for componente in componentes:
            self.stdout.write(f'  - {componente.nombre}')
        
        # Verificar estructuras de proyecto
        estructuras = EstructuraProyecto.objects.filter(activo=True).select_related('grupo', 'componente')
        self.stdout.write(f'\n🏗️  ESTRUCTURAS DE PROYECTO ACTIVAS ({estructuras.count()}):')
        total_incidencia = 0
        for estructura in estructuras:
            incidencia = float(estructura.incidencia)
            total_incidencia += incidencia
            self.stdout.write(f'  - {estructura.grupo.nombre} - {estructura.componente.nombre}: {incidencia}%')
        
        self.stdout.write(f'\n📈 TOTAL INCIDENCIA: {total_incidencia}%')
        
        # Verificar avances por sitio
        avances = AvanceProyecto.objects.filter(
            is_deleted=False,
            registro__sitio=sitio
        ).select_related('registro', 'proyecto', 'componente')
        
        self.stdout.write(f'\n📋 AVANCES PARA SITIO {sitio.name} ({avances.count()}):')
        
        if avances.count() == 0:
            self.stdout.write(self.style.WARNING('  ⚠️  No hay avances registrados para este sitio'))
        else:
            for avance in avances:
                proyecto_nombre = f"{avance.proyecto.grupo.nombre} - {avance.proyecto.componente.nombre}" if avance.proyecto else "Sin proyecto"
                self.stdout.write(f'  - {proyecto_nombre}:')
                self.stdout.write(f'    * Ejecución anterior: {float(avance.ejecucion_anterior)}%')
                self.stdout.write(f'    * Ejecución actual: {float(avance.ejecucion_actual)}%')
                self.stdout.write(f'    * Ejecución acumulada: {float(avance.ejecucion_acumulada)}%')
                self.stdout.write(f'    * Ejecución total: {float(avance.ejecucion_total)}%')
        
        # Simular cálculo de la vista
        self.stdout.write(f'\n🧮 SIMULACIÓN DEL CÁLCULO DE LA VISTA:')
        
        tabla_estructura = []
        total_ejecucion_calculado = 0
        
        for estructura in estructuras:
            # Obtener el último avance para esta estructura en este sitio
            ultimo_avance = AvanceProyecto.objects.filter(
                is_deleted=False,
                registro__sitio=sitio,
                proyecto=estructura
            ).order_by('-created_at').first()
            
            ejecucion_total = 0
            if ultimo_avance:
                ejecucion_total = float(ultimo_avance.ejecucion_total)
            
            tabla_estructura.append({
                'estructura': estructura,
                'componente': estructura.componente.nombre,
                'incidencia': float(estructura.incidencia),
                'ejecucion_total': ejecucion_total
            })
            
            total_ejecucion_calculado += ejecucion_total
            
            self.stdout.write(f'  - {estructura.grupo.nombre} - {estructura.componente.nombre}:')
            self.stdout.write(f'    * Incidencia: {float(estructura.incidencia)}%')
            self.stdout.write(f'    * Ejecución total: {ejecucion_total}%')
        
        self.stdout.write(f'\n📊 RESUMEN:')
        self.stdout.write(f'  - Total incidencia: {total_incidencia}%')
        self.stdout.write(f'  - Total ejecución calculado: {total_ejecucion_calculado}%')
        
        if total_ejecucion_calculado == 0:
            self.stdout.write(self.style.WARNING('  ⚠️  LA SUMA DE EJECUCIÓN TOTAL ES CERO'))
            self.stdout.write('  Posibles causas:')
            self.stdout.write('    1. No hay avances registrados para este sitio')
            self.stdout.write('    2. Todos los avances tienen ejecución_total = 0')
            self.stdout.write('    3. Los avances no están asociados a estructuras de proyecto')
        else:
            porcentaje = (total_ejecucion_calculado / total_incidencia * 100) if total_incidencia > 0 else 0
            self.stdout.write(f'  - Porcentaje de avance: {porcentaje:.1f}%')
        
        self.stdout.write('\n✅ Diagnóstico completado') 