"""
Vistas específicas de la API para la aplicación móvil.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from datetime import date
from django.contrib.auth import authenticate
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from .models import RegConstruccion, AvanceComponente, AvanceComponenteComentarios
from .serializers import (
    RegConstruccionSerializer,
    AvanceComponenteSerializer, AvanceComponenteComentariosSerializer
)
from core.models.sites import Site
from proyectos.models import Componente
from photos.models import Photos
import os
import requests


def get_tokens_for_user(user):
    """Genera tokens JWT para un usuario"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sitios_activos_por_usuario(request):
    """
    1. API para listar los sitios que están activos en reg_construccion filtrados por usuario.

    GET /api/v1/mobile/sitios-activos/?user_id=<id>
    """
    user_id = request.query_params.get('user_id')

    if not user_id:
        return Response(
            {'error': 'El parámetro user_id es requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user_id = int(user_id)
    except ValueError:
        return Response(
            {'error': 'user_id debe ser un número entero'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Obtener sitios únicos que tienen registros activos del usuario
    sitios_activos = Site.objects.filter(
        reg_construccion__user_id=user_id,
        reg_construccion__is_active=True
    ).distinct().values('id', 'name', 'pti_cell_id', 'operator_id')

    return Response({
        'sitios': list(sitios_activos),
        'total': sitios_activos.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fechas_por_usuario(request):
    """
    2. API para mostrar la lista de las fechas que tiene el usuario

    GET /api/v1/mobile/fechas-por-usuario/?user_id=<id>
    """
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response(
            {'error': 'El parámetro user_id es requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user_id = int(user_id)
    except ValueError:
        return Response(
            {'error': 'user_id debe ser un número entero'},
            status=status.HTTP_400_BAD_REQUEST
        )
    fechas = RegConstruccion.objects.filter(
        user_id=user_id, is_active=True).values('fecha')
    return Response({
        'fechas': list(fechas)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_nueva_fecha(request):
    """
    2. API para crear una nueva fecha (nuevo registro de construcción).

    POST /api/v1/mobile/crear-fecha/
    """
    try:
        # Validar datos requeridos
        required_fields = ['sitio_id', 'title', 'fecha']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {'error': f'El campo {field} es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Verificar que el sitio existe
        sitio = get_object_or_404(Site, id=request.data['sitio_id'])

        # Verificar que no existe un registro para la misma fecha, sitio y usuario
        fecha = request.data['fecha']
        registro_existente = RegConstruccion.objects.filter(
            sitio=sitio,
            user=request.user,
            fecha=fecha,
            is_active=True
        ).first()

        if registro_existente:
            return Response(
                {'error': f'Ya existe un registro para la fecha {fecha} en este sitio'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear el nuevo registro
        registro_data = {
            'sitio': sitio,
            'user': request.user,
            'title': request.data['title'],
            'description': request.data.get('description', ''),
            'fecha': fecha,
            'estado': request.data.get('estado', 'construccion'),
            'contratista_id': request.data.get('contratista_id'),
            'estructura_id': request.data.get('estructura_id'),
        }

        registro = RegConstruccion.objects.create(**registro_data)

        serializer = RegConstruccionSerializer(registro)
        return Response({
            'message': 'Registro creado exitosamente',
            'registro': serializer.data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': f'Error al crear el registro: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def llenar_objetivo(request):
    """
    3. API para llenar el campo objetivo.

    POST /api/v1/mobile/llenar-objetivo/
    """
    try:
        # Validar datos requeridos
        if 'registro_id' not in request.data or 'objetivo' not in request.data:
            return Response(
                {'error': 'Los campos registro_id y objetivo son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        registro_id = request.data['registro_id']
        objetivo_texto = request.data['objetivo']

        # Verificar que el registro existe y pertenece al usuario
        try:
            registro = RegConstruccion.objects.get(
                id=registro_id,
                user=request.user,
                is_active=True
            )
        except RegConstruccion.DoesNotExist:
            return Response(
                {'error': 'Registro no encontrado o no tienes permisos'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Crear o actualizar el objetivo
        objetivo, created = Objetivo.objects.get_or_create(
            registro=registro,
            is_deleted=False,
            defaults={'objetivo': objetivo_texto}
        )

        if not created:
            objetivo.objetivo = objetivo_texto
            objetivo.save()

        serializer = ObjetivoSerializer(objetivo)
        return Response({
            'message': 'Objetivo guardado exitosamente',
            'objetivo': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Error al guardar el objetivo: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def llenar_avance(request):
    """
    4. API para llenar el campo avance.

    POST /api/v1/mobile/llenar-avance/
    """
    try:
        # Validar datos requeridos
        required_fields = ['registro_id', 'componente_id', 'porcentaje_actual']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {'error': f'El campo {field} es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        registro_id = request.data['registro_id']
        componente_id = request.data['componente_id']
        porcentaje_actual = request.data['porcentaje_actual']
        porcentaje_acumulado = request.data.get('porcentaje_acumulado')
        comentarios = request.data.get('comentarios', '')
        fecha_avance = request.data.get('fecha', date.today())

        # Verificar que el registro existe y pertenece al usuario
        try:
            registro = RegConstruccion.objects.get(
                id=registro_id,
                user=request.user,
                is_active=True
            )
        except RegConstruccion.DoesNotExist:
            return Response(
                {'error': 'Registro no encontrado o no tienes permisos'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar que el componente existe
        try:
            componente = Componente.objects.get(id=componente_id)
        except Componente.DoesNotExist:
            return Response(
                {'error': 'Componente no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Crear o actualizar el avance
        avance, created = AvanceComponente.objects.get_or_create(
            registro=registro,
            componente=componente,
            fecha=fecha_avance,
            is_deleted=False,
            defaults={
                'porcentaje_actual': porcentaje_actual,
                'porcentaje_acumulado': porcentaje_acumulado,
                'comentarios': comentarios
            }
        )

        if not created:
            avance.porcentaje_actual = porcentaje_actual
            if porcentaje_acumulado:
                avance.porcentaje_acumulado = porcentaje_acumulado
            avance.comentarios = comentarios
            avance.save()

        serializer = AvanceComponenteSerializer(avance)
        return Response({
            'message': 'Avance guardado exitosamente',
            'avance': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Error al guardar el avance: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def llenar_tabla(request):
    """
    5. API para llenar la tabla (comentarios de avance por componente).

    POST /api/v1/mobile/llenar-tabla/
    """
    try:
        # Validar datos requeridos
        if 'registro_id' not in request.data or 'comentarios' not in request.data:
            return Response(
                {'error': 'Los campos registro_id y comentarios son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        registro_id = request.data['registro_id']
        comentarios_texto = request.data['comentarios']

        # Verificar que el registro existe y pertenece al usuario
        try:
            registro = RegConstruccion.objects.get(
                id=registro_id,
                user=request.user,
                is_active=True
            )
        except RegConstruccion.DoesNotExist:
            return Response(
                {'error': 'Registro no encontrado o no tienes permisos'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Crear o actualizar los comentarios
        comentarios_obj, created = AvanceComponenteComentarios.objects.get_or_create(
            registro=registro,
            is_deleted=False,
            defaults={'comentarios': comentarios_texto}
        )

        if not created:
            comentarios_obj.comentarios = comentarios_texto
            comentarios_obj.save()

        serializer = AvanceComponenteComentariosSerializer(comentarios_obj)
        return Response({
            'message': 'Comentarios guardados exitosamente',
            'comentarios': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Error al guardar los comentarios: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subir_imagenes(request):
    """
    6. API para subir imágenes.

    POST /api/v1/mobile/subir-imagenes/
    """
    try:
        # Validar datos requeridos
        if 'registro_id' not in request.data:
            return Response(
                {'error': 'El campo registro_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        registro_id = request.data['registro_id']

        # Verificar que el registro existe y pertenece al usuario
        try:
            registro = RegConstruccion.objects.get(
                id=registro_id,
                user=request.user,
                is_active=True
            )
        except RegConstruccion.DoesNotExist:
            return Response(
                {'error': 'Registro no encontrado o no tienes permisos'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Procesar las imágenes
        imagenes_subidas = []
        files = request.FILES.getlist('imagenes')

        if not files:
            return Response(
                {'error': 'No se encontraron imágenes para subir'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for imagen in files:
            # Crear el objeto Photos
            photo = Photos.objects.create(
                content_type=ContentType.objects.get_for_model(registro),
                object_id=registro.id,
                app='reg_construccion',
                etapa='general',
                imagen=imagen,
                descripcion=request.data.get('caption', '')
            )
            imagenes_subidas.append({
                'id': photo.id,
                'image_url': photo.imagen.url,
                'caption': photo.descripcion,
                'uploaded_at': photo.created_at.isoformat()
            })

        return Response({
            'message': f'{len(imagenes_subidas)} imágenes subidas exitosamente',
            'imagenes': imagenes_subidas
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': f'Error al subir las imágenes: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_registro_completo(request, registro_id):
    """
    API adicional para obtener un registro completo con todos sus datos.

    GET /api/v1/mobile/registro-completo/{registro_id}/
    """
    try:
        # Verificar que el registro existe y pertenece al usuario
        try:
            registro = RegConstruccion.objects.select_related(
                'sitio', 'user', 'contratista', 'estructura'
            ).prefetch_related(
                'objetivo_set', 'avancecomponente_set', 'avancecomponentecomentarios_set', 'ejecucionporcentajes_set'
            ).get(
                id=registro_id,
                user=request.user,
                is_active=True
            )
        except RegConstruccion.DoesNotExist:
            return Response(
                {'error': 'Registro no encontrado o no tienes permisos'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RegConstruccionSerializer(registro)
        return Response(serializer.data)

    except Exception as e:
        return Response(
            {'error': f'Error al obtener el registro: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    7. API para loguearse.

    POST /api/v1/mobile/login/
    """
    try:
        # Verificar que los datos estén disponibles
        if not request.data:
            return Response(
                {'error': 'No se recibieron datos en la petición'},
                status=status.HTTP_400_BAD_REQUEST
            )

        print(f"request.data: {request.data}")
        print(f"request.content_type: {request.content_type}")

        # Verificar que los campos requeridos estén presentes
        if 'username' not in request.data:
            return Response(
                {'error': 'El campo username es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if 'password' not in request.data:
            return Response(
                {'error': 'El campo password es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        username = request.data['username']
        password = request.data['password']

        # Validar que los campos no estén vacíos
        if not username or not password:
            return Response(
                {'error': 'Username y password no pueden estar vacíos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar si existe un sistema padre configurado
        parent_app_url = os.getenv('PARENT_SYSTEM_URL')
        if parent_app_url:
            # Autenticar contra el sistema padre
            parent_login_url = parent_app_url + '/api/v1/users/auth/login/'
            try:
                parent_response = requests.post(parent_login_url, data={
                    'username': username,
                    'password': password
                }, timeout=10)

                if parent_response.status_code == 200:
                    # Intentar parsear la respuesta del sistema padre
                    try:
                        parent_data = parent_response.json()
                    except:
                        # Si no es JSON válido, usar la respuesta como texto
                        parent_data = {
                            'message': 'Autenticación exitosa en sistema padre', 'raw_response': parent_response.text}

                    # Buscar o crear el usuario local
                    try:
                        user = User.objects.get(username=username)
                    except User.DoesNotExist:
                        # Si el usuario no existe localmente, crear uno básico
                        user = User.objects.create_user(
                            username=username,
                            email=username if '@' in username else '',
                            password='temp_password'  # Contraseña temporal
                        )

                    # Generar tokens JWT locales (no usar el token del sistema padre)
                    tokens = get_tokens_for_user(user)
                    return Response({
                        'message': 'Login exitoso (autenticado contra sistema padre)',
                        'user': user.id,
                        'username': user.username,
                        'parent_auth': parent_data,
                        'tokens': tokens  # Tokens JWT locales
                    })
                else:
                    # Si el sistema padre falla, intentar autenticación local como fallback
                    print(
                        f"Sistema padre falló con status {parent_response.status_code}, intentando autenticación local...")
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        tokens = get_tokens_for_user(user)
                        return Response({
                            'message': 'Login exitoso (autenticación local)',
                            'user': user.id,
                            'username': user.username,
                            'tokens': tokens
                        })
                    else:
                        return Response(
                            {'error': 'Credenciales incorrectas'},
                            status=status.HTTP_401_UNAUTHORIZED
                        )
            except requests.exceptions.RequestException as e:
                # Si hay error de conexión, intentar autenticación local como fallback
                print(
                    f"Error conectando con sistema padre: {str(e)}, intentando autenticación local...")
                user = authenticate(username=username, password=password)
                if user is not None:
                    tokens = get_tokens_for_user(user)
                    return Response({
                        'message': 'Login exitoso (autenticación local - sistema padre no disponible)',
                        'user': user.id,
                        'username': user.username,
                        'tokens': tokens
                    })
                else:
                    return Response(
                        {'error': 'Credenciales incorrectas'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
        else:
            # Autenticación local (fallback)
            user = authenticate(username=username, password=password)
            if user is not None:
                tokens = get_tokens_for_user(user)
                return Response({
                    'message': 'Login exitoso',
                    'user': user.id,
                    'username': user.username,
                    'tokens': tokens
                })
            else:
                return Response(
                    {'error': 'Usuario o contraseña incorrectos'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

    except Exception as e:
        return Response(
            {'error': f'Error al loguearse: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
