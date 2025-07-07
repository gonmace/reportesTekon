from rest_framework import serializers
from .models import Registros0
from core.models.sites import Site


class Registros0Serializer(serializers.ModelSerializer):
    sitio_nombre = serializers.CharField(source='sitio.name', read_only=True)
    
    class Meta:
        model = Registros0
        fields = ['id', 'sitio', 'sitio_nombre', 'fecha', 'descripcion', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SiteWithRegistroInicialSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    tiene_registro_inicial = serializers.SerializerMethodField()
    registro_inicial_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Site
        fields = '__all__'

    def get_user(self, obj):
        return obj.user.username if obj.user else None
    
    def get_tiene_registro_inicial(self, obj):
        """Verifica si el sitio tiene un registro inicial"""
        return obj.tiene_registro_inicial()
    
    def get_registro_inicial_id(self, obj):
        """Obtiene el ID del registro inicial si existe"""
        return obj.get_registro_inicial_id() 