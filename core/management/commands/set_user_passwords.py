"""
Comando para establecer contraseñas por defecto para usuarios después del reset de base de datos.
Uso: python manage.py set_user_passwords
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Establece contraseñas por defecto para usuarios después del reset de base de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default='123456',
            help='Contraseña por defecto para todos los usuarios (default: 123456)'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Contraseña para usuarios administradores (default: admin123)'
        )

    def handle(self, *args, **options):
        default_password = options['password']
        admin_password = options['admin_password']
        
        self.stdout.write('Estableciendo contraseñas por defecto para usuarios...')
        
        users = User.objects.all()
        updated_count = 0
        
        for user in users:
            try:
                # Usar contraseña de admin para superusuarios, contraseña normal para otros
                if user.is_superuser:
                    password = admin_password
                    password_type = 'admin'
                else:
                    password = default_password
                    password_type = 'normal'
                
                user.set_password(password)
                user.save()
                
                self.stdout.write(
                    f'  ✅ Usuario: {user.username} - Contraseña {password_type}: {password}'
                )
                updated_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ❌ Error estableciendo contraseña para {user.username}: {e}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nContraseñas establecidas para {updated_count} usuarios:\n'
                f'  • Usuarios normales: {default_password}\n'
                f'  • Administradores: {admin_password}\n'
                f'\n⚠️  IMPORTANTE: Cambia estas contraseñas después del primer acceso.'
            )
        ) 