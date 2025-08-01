"""
Comando para probar la creación automática de AvanceProyecto.
"""

from django.core.management.base import BaseCommand
from users.models import User
from core.models.sites import Site
from reg_visita.models import RegVisita, AvanceProyecto
from proyectos.models import EstructuraProyecto, Componente, Grupo
import random


class Command(BaseCommand):
    help = 'Prueba la creación automática de AvanceProyecto cuando se crea un RegVisita'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-data',
            action='store_true',
            help='Crear datos de prueba si no existen'
        )

    def handle(self, *args, **options):
        create_data = options['create_data']
        
        self.stdout.write(
            self.style.SUCCESS('Iniciando prueba de creación automática de AvanceProyecto...')
        )
        
        # Crear datos de prueba si se solicita
        if create_data:
            self.create_test_data()
        
        # Verificar que existen datos necesarios
        if not self.check_required_data():
            self.stdout.write(
                self.style.ERROR('Faltan datos requeridos. Ejecuta con --create-data para crearlos.')
            )
            return
        
        # Crear un registro de visita de prueba
        self.stdout.write('Creando registro de visita de prueba...')
        
        try:
            # Obtener datos existentes
            user = User.objects.first()
            site = Site.objects.first()
            
            if not user or not site:
                self.stdout.write(
                    self.style.ERROR('No hay usuarios o sitios disponibles.')
                )
                return
            
            # Crear registro de visita
            registro = RegVisita.objects.create(
                sitio=site,
                user=user,
                title='Prueba de Avance Automático',
                description='Registro de prueba para verificar la creación automática de AvanceProyecto',
                fecha='2025-01-29'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Registro de visita creado: {registro.id}')
            )
            
            # Verificar si se creó automáticamente el AvanceProyecto
            avances = AvanceProyecto.objects.filter(registro=registro)
            
            if avances.exists():
                avance = avances.first()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ AvanceProyecto creado automáticamente:\n'
                        f'   ID: {avance.id}\n'
                        f'   Registro: {avance.registro.title}\n'
                        f'   Proyecto: {avance.proyecto}\n'
                        f'   Componente: {avance.componente}\n'
                        f'   Ejecución Total: {avance.ejecucion_total}%'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ No se creó automáticamente el AvanceProyecto')
                )
            
            # Mostrar estadísticas
            self.stdout.write('\n📊 Estadísticas:')
            self.stdout.write(f'   Total RegVisita: {RegVisita.objects.count()}')
            self.stdout.write(f'   Total AvanceProyecto: {AvanceProyecto.objects.count()}')
            self.stdout.write(f'   Avances para este registro: {avances.count()}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error durante la prueba: {e}')
            )
    
    def create_test_data(self):
        """Crear datos de prueba necesarios."""
        self.stdout.write('Creando datos de prueba...')
        
        # Crear usuario de prueba
        user, created = User.objects.get_or_create(
            username='test_user_avance',
            defaults={
                'email': 'test_avance@example.com',
                'first_name': 'Usuario',
                'last_name': 'Prueba Avance',
                'is_staff': True,
                'is_active': True
            }
        )
        
        if created:
            user.set_password('test123')
            user.save()
            self.stdout.write('Usuario de prueba creado')
        
        # Crear sitio de prueba con coordenadas únicas
        import random
        lat = -33.4489 + random.uniform(-0.01, 0.01)
        lon = -70.6693 + random.uniform(-0.01, 0.01)
        
        site, created = Site.objects.get_or_create(
            name='Sitio Prueba Avance',
            defaults={
                'pti_cell_id': f'PTI_AVANCE_{random.randint(1000, 9999)}',
                'operator_id': f'OP_AVANCE_{random.randint(1000, 9999)}',
                'lat_base': lat,
                'lon_base': lon,
                'alt': 500,
                'region': 'Metropolitana',
                'comuna': 'Santiago'
            }
        )
        
        if created:
            self.stdout.write('Sitio de prueba creado')
        
        # Crear grupo de prueba
        grupo, created = Grupo.objects.get_or_create(
            nombre='Grupo Prueba Avance',
            defaults={
                'descripcion': 'Grupo de prueba para avances automáticos',
                'activo': True
            }
        )
        
        if created:
            self.stdout.write('Grupo de prueba creado')
        
        # Crear componente de prueba
        componente, created = Componente.objects.get_or_create(
            nombre='Componente Prueba Avance',
            defaults={
                'descripcion': 'Componente de prueba para avances automáticos',
                'activo': True
            }
        )
        
        if created:
            self.stdout.write('Componente de prueba creado')
        
        # Crear estructura de proyecto de prueba
        estructura, created = EstructuraProyecto.objects.get_or_create(
            grupo=grupo,
            componente=componente,
            defaults={
                'incidencia': 25.00,
                'orden': 1,
                'sort_order': 1,
                'activo': True
            }
        )
        
        if created:
            self.stdout.write('Estructura de proyecto de prueba creada')
        
        self.stdout.write(
            self.style.SUCCESS('✅ Datos de prueba creados exitosamente')
        )
    
    def check_required_data(self):
        """Verificar que existen los datos requeridos."""
        has_user = User.objects.exists()
        has_site = Site.objects.exists()
        has_estructura = EstructuraProyecto.objects.filter(activo=True).exists()
        
        if not has_user:
            self.stdout.write(self.style.WARNING('⚠️  No hay usuarios en la base de datos'))
        
        if not has_site:
            self.stdout.write(self.style.WARNING('⚠️  No hay sitios en la base de datos'))
        
        if not has_estructura:
            self.stdout.write(self.style.WARNING('⚠️  No hay estructuras de proyecto activas'))
        
        return has_user and has_site 