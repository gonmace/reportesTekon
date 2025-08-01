"""
Comando para crear datos de prueba para reg_visita.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models.sites import Site
from reg_visita.models import RegVisita, AvanceProyecto
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea datos de prueba para reg_visita'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Número de registros de avance de proyecto a crear'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(
            self.style.SUCCESS(f'Creando {count} registros de prueba para AvanceProyecto...')
        )
        
        # Obtener o crear usuario de prueba
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Usuario',
                'last_name': 'Prueba',
                'is_staff': True,
                'is_active': True
            }
        )
        
        if created:
            user.set_password('test123')
            user.save()
            self.stdout.write(
                self.style.SUCCESS('Usuario de prueba creado: test_user / test123')
            )
        
        # Obtener o crear sitio de prueba
        site, created = Site.objects.get_or_create(
            name='Sitio de Prueba',
            defaults={
                'pti_cell_id': 'PTI001',
                'operator_id': 'OP001',
                'lat_base': -33.4489,
                'lon_base': -70.6693,
                'alt': 500,
                'region': 'Metropolitana',
                'comuna': 'Santiago'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Sitio de prueba creado: Sitio de Prueba')
            )
        
        # Obtener o crear registro de visita
        registro, created = RegVisita.objects.get_or_create(
            title='Reporte de Visita de Prueba',
            defaults={
                'sitio': site,
                'user': user,
                'description': 'Reporte de visita para pruebas de la tabla editable'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Registro de visita creado')
            )
        
        # Obtener estructuras de proyecto y componentes
        try:
            from proyectos.models import EstructuraProyecto, Componente
            
            # Crear estructuras de proyecto de prueba si no existen
            estructuras_proyecto = []
            for i in range(3):
                estructura, created = EstructuraProyecto.objects.get_or_create(
                    nombre=f'Estructura Proyecto {i+1}',
                    defaults={
                        'descripcion': f'Descripción de la estructura de proyecto {i+1}',
                        'activo': True,
                        'orden': i+1
                    }
                )
                estructuras_proyecto.append(estructura)
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Estructura de proyecto creada: {estructura.nombre}')
                    )
            
            # Crear componentes de prueba si no existen
            componentes = []
            for i in range(4):
                componente, created = Componente.objects.get_or_create(
                    nombre=f'Componente {i+1}',
                    defaults={
                        'descripcion': f'Descripción del componente {i+1}',
                        'activo': True,
                        'orden': i+1
                    }
                )
                componentes.append(componente)
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Componente creado: {componente.nombre}')
                    )
            
        except ImportError:
            self.stdout.write(
                self.style.WARNING('No se pudo importar modelos de proyectos. Creando datos sin relaciones.')
            )
            estructuras_proyecto = [None] * 3
            componentes = [None] * 4
        
        # Crear registros de avance de proyecto
        comentarios_ejemplo = [
            'Avance significativo en la construcción de la estructura principal',
            'Completado el 60% de la obra civil',
            'Instalaciones eléctricas en progreso',
            'Sistema de drenaje terminado',
            'Pavimentación en etapa final',
            'Instalación de equipos mecánicos',
            'Paisajismo y áreas verdes en desarrollo',
            'Sistema de seguridad implementado',
            'Pruebas de funcionamiento en curso',
            'Documentación técnica actualizada'
        ]
        
        for i in range(count):
            # Generar porcentajes aleatorios pero realistas
            ejecucion_anterior = Decimal(str(random.randint(0, 80)))
            ejecucion_actual = Decimal(str(random.randint(5, 25)))
            ejecucion_acumulada = ejecucion_anterior + ejecucion_actual
            ejecucion_total = min(ejecucion_acumulada + Decimal(str(random.randint(0, 10))), Decimal('100'))
            
            avance = AvanceProyecto.objects.create(
                registro=registro,
                proyecto=random.choice(estructuras_proyecto) if estructuras_proyecto[0] else None,
                componente=random.choice(componentes) if componentes[0] else None,
                comentarios=random.choice(comentarios_ejemplo),
                ejecucion_anterior=ejecucion_anterior,
                ejecucion_actual=ejecucion_actual,
                ejecucion_acumulada=ejecucion_acumulada,
                ejecucion_total=ejecucion_total
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Avance de proyecto {i+1} creado: {avance.id}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Datos de prueba creados exitosamente!\n'
                f'📊 Se crearon {count} registros de AvanceProyecto\n'
                f'👤 Usuario: test_user / test123\n'
                f'🏢 Sitio: Sitio de Prueba\n'
                f'📋 Registro: Reporte de Visita de Prueba\n\n'
                f'🔗 Puedes acceder a la tabla editable en:\n'
                f'   http://localhost:8000/reg_visita/avances_proyecto/\n'
                f'   http://localhost:8000/reg_visita/1/steps/\n'
            )
        ) 