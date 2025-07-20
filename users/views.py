from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer

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
