"""
Comando para crear un superusuario por defecto.
Uso: python manage.py create_default_superuser
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea un superusuario por defecto para el sistema'

    def handle(self, *args, **options):
        username = 'gonzalo'
        email = 'gonzalo@tekon.com'
        password = 'ojalaque'
        
        # Verificar si ya existe un superusuario
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING(
                    'Ya existe un superusuario en el sistema. '
                    'Usando credenciales por defecto:'
                )
            )
            self.stdout.write(f'  Usuario: {username}')
            self.stdout.write(f'  Contraseña: {password}')
            return
        
        # Crear superusuario
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Administrador',
                last_name='Sistema'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superusuario creado exitosamente!\n'
                    f'Usuario: {username}\n'
                    f'Email: {email}\n'
                    f'Contraseña: {password}\n'
                    f'ID: {user.id}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error al crear superusuario: {e}'
                )
            ) 