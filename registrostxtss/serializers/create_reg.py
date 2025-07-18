from rest_framework import serializers
from registrostxtss.models.registrostxtss import RegistrosTxTss
from core.models.sites import Site
from users.models import User
from core.serializers import SiteSerializer
from users.serializers import UserSerializer


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
        fields = ['id', 'sitio', 'sitio_id', 'user', 'user_id', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Asegurar que registro sea un booleano
        validated_data['is_deleted'] = bool(validated_data.get('is_deleted', False))
        try:
            return super().create(validated_data)
        except Exception as e:
            # Capturar error de restricción única y personalizar mensaje
            if 'unique_sitio_user_combination' in str(e):
                from django.core.exceptions import ValidationError
                raise ValidationError({
                    'non_field_errors': ['Ya existe un registro para este sitio y usuario. No se puede crear un registro duplicado.']
                })
            raise e 