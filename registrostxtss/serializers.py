from rest_framework import serializers
from .models.registros import RegistrosTxTss
from core.models.sites import Site
from users.models import User

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'pti_cell_id', 'operator_id', 'name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class RegistrosTxTssSerializer(serializers.ModelSerializer):
    sitio = SiteSerializer(read_only=True)
    sitio_id = serializers.PrimaryKeyRelatedField(
        queryset=Site.objects.all(),
        source='sitio',
        write_only=True
    )
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type=User.ITO),
        source='user',
        write_only=True
    )
    
    class Meta:
        model = RegistrosTxTss
        fields = ['id', 'sitio', 'sitio_id', 'user', 'user_id', 'registro0', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Asegurar que registro0 sea un booleano
        validated_data['registro0'] = bool(validated_data.get('registro0', False))
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Asegurar que registro0 sea un booleano
        if 'registro0' in validated_data:
            validated_data['registro0'] = bool(validated_data['registro0'])
        return super().update(instance, validated_data) 