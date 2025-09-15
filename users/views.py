from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer
import os

# Create your views here.


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para usuarios, específicamente ITOs.
    """
    queryset = User.objects.filter(user_type=User.ITO)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def usuarios_ito(self, request):
        """
        Endpoint específico para obtener usuarios ITO.
        """
        usuarios = self.queryset
        serializer = self.get_serializer(usuarios, many=True)
        return Response(serializer.data)


@login_required
def logout_view(request):
    """
    Vista para cerrar sesión del usuario.
    Redirige al login de la URL padre si está configurada.
    """
    # Obtener la URL del sistema padre desde las variables de entorno
    parent_system_url = os.getenv('PARENT_SYSTEM_URL')

    # Cerrar sesión
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')

    # Si hay una URL padre configurada, redirigir al login de la URL padre
    if parent_system_url:
        # Construir la URL de login del sistema padre
        parent_login_url = f"{parent_system_url}/auth/login/"
        return redirect(parent_login_url)

    # Si no hay URL padre, redirigir al login local
    return redirect('users:login')
