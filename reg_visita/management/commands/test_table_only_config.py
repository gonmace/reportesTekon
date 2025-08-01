"""
Comando para probar la funcionalidad de create_table_only_config.
"""

from django.core.management.base import BaseCommand
from users.models import User
from core.models.sites import Site
from reg_visita.models import RegVisita, AvanceProyecto
from proyectos.models import EstructuraProyecto, Componente, Grupo
from reg_visita.config import REGISTRO_CONFIG
import random


class Command(BaseCommand):
    help = 'Prueba la funcionalidad de create_table_only_config y creación automática de AvanceProyecto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-data',
            action='store_true',
            help='Crear datos de prueba si no existen'
        )

    def handle(self, *args, **options):
        create_data = options['create_data']
        
        self.stdout.write(
            self.style.SUCCESS('Iniciando prueba de create_table_only_config...')
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
        
        # Probar la configuración de tabla editable
        self.test_table_only_config()
        
        # Probar la creación automática de AvanceProyecto
        self.test_automatic_avance_creation()
    
    def test_table_only_config(self):
        """Probar la configuración de tabla editable."""
        self.stdout.write('\n🔧 Probando configuración de tabla editable...')
        
        try:
            # Verificar que la configuración existe
            if hasattr(REGISTRO_CONFIG, 'pasos_config'):
                pasos = REGISTRO_CONFIG.pasos_config
                
                if 'avance_proyecto' in pasos:
                    paso_config = pasos['avance_proyecto']
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Configuración de tabla editable encontrada:\n'
                            f'   Título: {paso_config.title}\n'
                            f'   Descripción: {paso_config.description}\n'
                            f'   Tipo: {type(paso_config).__name__}'
                        )
                    )
                    
                    # Verificar que tiene sub_elementos
                    if hasattr(paso_config, 'elemento') and paso_config.elemento:
                        elemento = paso_config.elemento
                        if hasattr(elemento, 'sub_elementos') and elemento.sub_elementos:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'   Sub-elementos: {len(elemento.sub_elementos)}'
                                )
                            )
                            
                            for i, sub_elemento in enumerate(elemento.sub_elementos):
                                self.stdout.write(
                                    f'     {i+1}. Tipo: {sub_elemento.tipo}\n'
                                    f'        Título: {sub_elemento.title}\n'
                                    f'        API URL: {sub_elemento.config.get("api_url", "No definida")}'
                                )
                        else:
                            self.stdout.write(
                                self.style.WARNING('⚠️  No hay sub_elementos configurados')
                            )
                    else:
                        self.stdout.write(
                            self.style.WARNING('⚠️  No hay elemento configurado')
                        )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ No se encontró la configuración "avance_proyecto"')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ No se encontró la configuración de pasos')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al probar configuración: {e}')
            )
    
    def test_automatic_avance_creation(self):
        """Probar la creación automática de AvanceProyecto."""
        self.stdout.write('\n🔄 Probando creación automática de AvanceProyecto...')
        
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
                title='Prueba Table Only Config',
                description='Registro de prueba para verificar create_table_only_config',
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
                
                # Verificar que el avance está vinculado correctamente
                if avance.proyecto:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'   ✅ Vinculado a proyecto: {avance.proyecto.grupo.nombre} - {avance.proyecto.componente.nombre}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️  No hay proyecto asignado')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ No se creó automáticamente el AvanceProyecto')
                )
            
            # Mostrar estadísticas
            self.stdout.write('\n📊 Estadísticas finales:')
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
            username='test_user_table_only',
            defaults={
                'email': 'test_table_only@example.com',
                'first_name': 'Usuario',
                'last_name': 'Prueba Table Only',
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
            name='Sitio Prueba Table Only',
            defaults={
                'pti_cell_id': f'PTI_TABLE_{random.randint(1000, 9999)}',
                'operator_id': f'OP_TABLE_{random.randint(1000, 9999)}',
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
            nombre='Grupo Prueba Table Only',
            defaults={
                'descripcion': 'Grupo de prueba para table only config',
                'activo': True
            }
        )
        
        if created:
            self.stdout.write('Grupo de prueba creado')
        
        # Crear componente de prueba
        componente, created = Componente.objects.get_or_create(
            nombre='Componente Prueba Table Only',
            defaults={
                'descripcion': 'Componente de prueba para table only config',
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
                'incidencia': 30.00,
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