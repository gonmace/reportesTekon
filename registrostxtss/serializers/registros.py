from rest_framework import serializers
from registrostxtss.models.r_sitio import RSitio

class RSitioSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = RSitio
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

