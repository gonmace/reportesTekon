"""
Comando para crear grupos de actividades de ejemplo.
"""

from django.core.management.base import BaseCommand
from proyectos.models import Grupo, Componente, GrupoComponente


class Command(BaseCommand):
    help = 'Crea grupos de actividades de ejemplo para probar la funcionalidad'

    def handle(self, *args, **options):
        self.stdout.write('Creando grupos de actividades de ejemplo...')
        
        # Obtener todos los componentes disponibles
        componentes = Componente.objects.all()
        if not componentes.exists():
            self.stdout.write(self.style.ERROR('❌ No hay componentes disponibles. Ejecuta primero: python manage.py crear_componentes'))
            return
        
        # Crear grupos de actividades
        grupos_data = [
            {
                'nombre': 'Torres Completas',
                'descripcion': 'Grupo completo con todos los componentes para torres grandes',
                'orden': 1,
                'componentes': [
                    ('Instalación de faenas', 5.0),
                    ('Replanteo y Trazado', 5.0),
                    ('Excavación para la fundación', 5.0),
                    ('Enferradura de la fundación', 15.0),
                    ('Hormigonado de la fundación', 15.0),
                    ('Relleno y compactado', 5.0),
                    ('Montaje de la Torre', 15.0),
                    ('Losa Radier de Equipos', 5.0),
                    ('Cierre perimetral', 5.0),
                    ('Sistema puesta a tierra', 5.0),
                    ('Sistema Eléctrico', 5.0),
                    ('Linea Electica definitiva', 10.0),
                    ('Trabajos Finales / Adicionales', 5.0),
                ]
            },
            {
                'nombre': 'Torres Pequeñas',
                'descripcion': 'Grupo reducido con la mitad de componentes para torres pequeñas',
                'orden': 2,
                'componentes': [
                    ('Instalación de faenas', 10.0),
                    ('Replanteo y Trazado', 10.0),
                    ('Excavación para la fundación', 15.0),
                    ('Enferradura de la fundación', 20.0),
                    ('Hormigonado de la fundación', 20.0),
                    ('Montaje de la Torre', 15.0),
                    ('Sistema Eléctrico', 10.0),
                ]
            },
            {
                'nombre': 'Fundaciones',
                'descripcion': 'Grupo especializado solo en trabajos de fundación',
                'orden': 3,
                'componentes': [
                    ('Replanteo y Trazado', 10.0),
                    ('Excavación para la fundación', 25.0),
                    ('Enferradura de la fundación', 35.0),
                    ('Hormigonado de la fundación', 30.0),
                ]
            },
            {
                'nombre': 'Sistemas Eléctricos',
                'descripcion': 'Grupo especializado en sistemas eléctricos',
                'orden': 4,
                'componentes': [
                    ('Sistema puesta a tierra', 30.0),
                    ('Sistema Eléctrico', 40.0),
                    ('Linea Electica definitiva', 30.0),
                ]
            }
        ]
        
        grupos_creados = 0
        for grupo_data in grupos_data:
            grupo, created = Grupo.objects.get_or_create(
                nombre=grupo_data['nombre'],
                defaults={
                    'descripcion': grupo_data['descripcion'],
                    'orden': grupo_data['orden']
                }
            )
            if created:
                self.stdout.write(f'✓ Grupo creado: {grupo.nombre}')
                grupos_creados += 1
            else:
                self.stdout.write(f'⚠ Grupo ya existe: {grupo.nombre}')
            
            # Asignar componentes al grupo con sus pesos
            componentes_asignados = 0
            for nombre_componente, porcentaje in grupo_data['componentes']:
                componente = componentes.filter(nombre=nombre_componente).first()
                if componente:
                    grupo_comp, created = GrupoComponente.objects.get_or_create(
                        grupo=grupo,
                        componente=componente,
                        defaults={
                            'porcentaje_incidencia': porcentaje,
                            'orden': len(grupo_data['componentes']) - grupo_data['componentes'].index((nombre_componente, porcentaje))
                        }
                    )
                    if created:
                        self.stdout.write(f'  ✓ Componente asignado: {componente.nombre} ({porcentaje}%)')
                        componentes_asignados += 1
                    else:
                        self.stdout.write(f'  ⚠ Componente ya asignado: {componente.nombre}')
                else:
                    self.stdout.write(f'  ❌ Componente no encontrado: {nombre_componente}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Proceso completado!\n'
                f'• {grupos_creados} grupos nuevos creados\n'
                f'• {len(grupos_data) - grupos_creados} grupos ya existían\n'
                f'• Total de grupos: {Grupo.objects.count()}\n'
                f'• Total de relaciones grupo-componente: {GrupoComponente.objects.count()}'
            )
        ) 