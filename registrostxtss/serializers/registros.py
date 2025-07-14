from rest_framework import serializers
from core.models.sites import Site
from core.serializers import SiteSerializer
from users.models import User
from users.serializers import UserSerializer
from registrostxtss.models.main_registrostxtss import RegistrosTxTss
from registrostxtss.models.r_sitio import Registros0

class Registros0Serializer(serializers.ModelSerializer):
    
    class Meta:
        model = Registros0
        fields = ['id', 'sitio', 'sitio_id', 'lat', 'lon', 'altura', 'dimensiones', 'deslindes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except Exception as e:
            # Capturar errores de validación y personalizar mensajes
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'non_field_errors': ['Error al crear el registro. Verifica que todos los campos sean válidos.']
            })

