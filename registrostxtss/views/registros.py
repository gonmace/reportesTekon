from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from registrostxtss.models.main_registrostxtss import RegistrosTxTss
from registrostxtss.models.r_sitio import Registros0
from registrostxtss.serializers.registros import Registros0Serializer
from registrostxtss.serializers.create import RegistrosTxTssSerializer
from users.models import User



class RegistrosTxTssViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para manejar todas las operaciones de RegistrosTxTss
    """
    queryset = RegistrosTxTss.objects.all()
    serializer_class = RegistrosTxTssSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['sitio__name', 'user__username', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'updated_at', 'sitio__name', 'user__username']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """
        Personalizar la creación del registro
        """
        serializer.save()

    @action(detail=True, methods=['put'])
    def activar(self, request, pk=None):
        """
        Endpoint personalizado para activar un registro
        """
        registro = self.get_object()
        registro.activar_registro()
        serializer = self.get_serializer(registro)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_sitio(self, request):
        """
        Endpoint para filtrar registros por sitio
        """
        sitio_id = request.query_params.get('sitio_id')
        if sitio_id:
            registros = self.queryset.filter(sitio_id=sitio_id)
            serializer = self.get_serializer(registros, many=True)
            return Response(serializer.data)
        return Response({'error': 'sitio_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def por_usuario(self, request):
        """
        Endpoint para filtrar registros por usuario
        """
        user_id = request.query_params.get('user_id')
        if user_id:
            registros = self.queryset.filter(user_id=user_id)
            serializer = self.get_serializer(registros, many=True)
            return Response(serializer.data)
        return Response({'error': 'user_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def activos(self, request):
        """
        Endpoint para obtener solo registros activos
        """
        registros = self.queryset.filter(registro0=True)
        serializer = self.get_serializer(registros, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def inactivos(self, request):
        """
        Endpoint para obtener solo registros inactivos
        """
        registros = self.queryset.filter(registro0=False)
        serializer = self.get_serializer(registros, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sitio(self, request, sitio_id=None):
        """
        Endpoint para obtener registros de un sitio específico por URL
        """
        if sitio_id:
            registros = self.queryset.filter(sitio_id=sitio_id)
            serializer = self.get_serializer(registros, many=True)
            return Response(serializer.data)
        return Response({'error': 'sitio_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def usuario(self, request, user_id=None):
        """
        Endpoint para obtener registros de un usuario específico por URL
        """
        if user_id:
            registros = self.queryset.filter(user_id=user_id)
            serializer = self.get_serializer(registros, many=True)
            return Response(serializer.data)
        return Response({'error': 'user_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def usuarios_ito(self, request):
        """
        Endpoint para obtener lista de usuarios ITO disponibles
        """
        usuarios_ito = User.objects.filter(
            user_type=User.ITO,
            is_active=True,
            is_deleted=False
        ).values('id', 'username', 'first_name', 'last_name')
        
        return Response(list(usuarios_ito))
