import jwt
import logging
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from .models import User

logger = logging.getLogger(__name__)


class JWTAutoAuthMiddleware:
    """
    Middleware para autenticación automática con JWT.
    Verifica si hay un token JWT en los parámetros de la URL y autentica automáticamente al usuario.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo procesar en rutas específicas que requieren autenticación automática
        if self._should_process_request(request):
            token = request.GET.get('token')

            if token and not request.user.is_authenticated:
                try:
                    # Decodificar el token JWT
                    if settings.JWT_SECRET_KEY and settings.JWT_SECRET_KEY != 'default-secret-key-change-in-production':
                        # Verificar firma del token
                        payload = jwt.decode(
                            token,
                            settings.JWT_SECRET_KEY,
                            algorithms=[settings.JWT_ALGORITHM],
                            audience=settings.JWT_AUDIENCE,
                            issuer=settings.JWT_ISSUER
                        )
                    else:
                        # Modo desarrollo: decodificar sin verificar firma
                        payload = jwt.decode(
                            token, options={"verify_signature": False})

                    # Extraer datos del usuario - manejar diferentes formatos de token
                    if 'user' in payload:
                        # Formato esperado: {"user": {...}}
                        user_data = payload.get('user', {})
                    else:
                        # Formato alternativo: datos directamente en el payload
                        user_data = {
                            'username': payload.get('username'),
                            'email': payload.get('email'),
                            'first_name': payload.get('first_name'),
                            'last_name': payload.get('last_name'),
                            'user_type': payload.get('user_type'),
                            'phone': payload.get('phone', ''),
                        }

                    username = user_data.get('username')

                    if username:
                        # Buscar o crear el usuario
                        user, created = User.objects.get_or_create(
                            username=username,
                            defaults={
                                'email': user_data.get('email', f'{username}@tekon.com'),
                                'first_name': user_data.get('first_name', ''),
                                'last_name': user_data.get('last_name', ''),
                                'user_type': user_data.get('user_type', User.ITO),
                                'phone': user_data.get('phone', ''),
                                'is_active': True,
                            }
                        )

                        # Si el usuario ya existía, actualizar sus datos
                        if not created:
                            user.email = user_data.get('email', user.email)
                            user.first_name = user_data.get(
                                'first_name', user.first_name)
                            user.last_name = user_data.get(
                                'last_name', user.last_name)
                            user.user_type = user_data.get(
                                'user_type', user.user_type)
                            user.phone = user_data.get('phone', user.phone)
                            user.is_active = True
                            user.save()

                        # Autenticar al usuario
                        login(request, user)

                        logger.info(
                            f"Usuario {username} autenticado automáticamente via middleware. Creado: {created}")

                        # Limpiar el token de la URL para evitar reutilización
                        from django.http import QueryDict
                        query_dict = QueryDict(
                            request.GET.urlencode(), mutable=True)
                        query_dict.pop('token', None)

                        # Redirigir sin el token en la URL
                        if query_dict:
                            redirect_url = f"{request.path}?{query_dict.urlencode()}"
                        else:
                            redirect_url = request.path

                        return redirect(redirect_url)

                except jwt.InvalidTokenError as e:
                    logger.warning(f"Token JWT inválido en middleware: {e}")
                except Exception as e:
                    logger.error(
                        f"Error en middleware de autenticación automática: {e}")

        response = self.get_response(request)
        return response

    def _should_process_request(self, request):
        """
        Determina si el middleware debe procesar esta petición.
        """
        path = request.path

        # Solo procesar peticiones GET principales (no archivos estáticos, media, etc.)
        if request.method != 'GET':
            return False

        # Rutas que NO deben procesarse (tienen prioridad)
        exclude_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/api/',
            '/__reload__/',
        ]

        # Verificar si la ruta está en la lista de exclusión
        for exclude_path in exclude_paths:
            if path.startswith(exclude_path):
                return False

        # Rutas que permiten autenticación automática
        auto_auth_paths = [
            '/',  # Ruta principal
            '/dashboard/',
            '/sitios/',
            '/reg_txtss/',
            '/reg_visita/',
            '/proyectos/',
        ]

        # Verificar si la ruta está en la lista de autenticación automática
        for auth_path in auto_auth_paths:
            if path == auth_path or (auth_path != '/' and path.startswith(auth_path)):
                return True

        return False
