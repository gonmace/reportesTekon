from rest_framework import serializers
from .models.registro import Registros
from core.models.sites import Site
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class SiteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Site
        fields = ['id', 'name', 'pti_cell_id', 'operator_id']

class RegistrosSerializer(serializers.ModelSerializer):
    sitio = SiteSerializer(read_only=True)
    
    class Meta:
        model = Registros
        fields = ['id', 'sitio', 'registro0', 'registro1', 'registro2', 'created_at', 'updated_at']

# Serializador que combina ambos modelos
class SiteWithRegistrosSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    registro0 = serializers.SerializerMethodField()
    registro1 = serializers.SerializerMethodField()
    registro2 = serializers.SerializerMethodField()
    
    class Meta:
        model = Site
        fields = ['id', 'name', 'pti_cell_id', 'operator_id', 'user', 'registro0', 'registro1', 'registro2']

    def get_registro0(self, obj):
        try:
            registro = Registros.objects.get(sitio=obj)
            return registro.registro0
        except Registros.DoesNotExist:
            return None

    def get_registro1(self, obj):
        try:
            registro = Registros.objects.get(sitio=obj)
            return registro.registro1
        except Registros.DoesNotExist:
            return None

    def get_registro2(self, obj):
        try:
            registro = Registros.objects.get(sitio=obj)
            return registro.registro2
        except Registros.DoesNotExist:
            return None



















# Ejemplo usando SerializerMethodField para datos personalizados
class CombinedDataSerializer(serializers.ModelSerializer):
    sitio_info = serializers.SerializerMethodField()
    registros_info = serializers.SerializerMethodField()
    usuario_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Site
        fields = ['sitio_info', 'registros_info', 'usuario_info']
    
    def get_sitio_info(self, obj):
        return {
            'id': obj.id,
            'nombre': obj.name,
            'pti_id': obj.pti_cell_id,
            'operador_id': obj.operator_id,
            'region': obj.region,
            'comuna': obj.comuna
        }
    
    def get_registros_info(self, obj):
        try:
            registro = Registros.objects.get(sitio=obj)
            return {
                'tiene_registro0': registro.registro0,
                'tiene_registro1': registro.registro1,
                'tiene_registro2': registro.registro2,
                'fecha_creacion': registro.created_at.strftime('%d/%m/%Y'),
                'ultima_actualizacion': registro.updated_at.strftime('%d/%m/%Y %H:%M')
            }
        except Registros.DoesNotExist:
            return {'mensaje': 'No hay registros asociados'}
    
    def get_usuario_info(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'nombre_completo': f"{obj.user.first_name} {obj.user.last_name}",
                'tipo_usuario': obj.user.user_type,
                'telefono': obj.user.phone
            }
        return {'mensaje': 'No hay usuario asignado'}

# Serializador optimizado con select_related y prefetch_related
class OptimizedSiteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    registros_count = serializers.SerializerMethodField()
    ultimo_registro = serializers.SerializerMethodField()
    
    class Meta:
        model = Site
        fields = ['id', 'name', 'pti_cell_id', 'operator_id', 'region', 'comuna', 'user', 'registros_count', 'ultimo_registro']
    
    def get_registros_count(self, obj):
        return Registros.objects.filter(sitio=obj).count()
    
    def get_ultimo_registro(self, obj):
        try:
            ultimo = Registros.objects.filter(sitio=obj).latest('created_at')
            return {
                'id': ultimo.id,
                'fecha': ultimo.created_at.strftime('%d/%m/%Y %H:%M'),
                'registros_completados': sum([ultimo.registro0, ultimo.registro1, ultimo.registro2])
            }
        except Registros.DoesNotExist:
            return None

# Serializador para crear/actualizar con validación de múltiples modelos
class SiteRegistrosCreateSerializer(serializers.ModelSerializer):
    registros_data = serializers.DictField(write_only=True, required=False)
    
    class Meta:
        model = Site
        fields = ['name', 'pti_cell_id', 'operator_id', 'region', 'comuna', 'user', 'registros_data']
    
    def create(self, validated_data):
        registros_data = validated_data.pop('registros_data', {})
        site = Site.objects.create(**validated_data)
        
        # Crear registro asociado
        if registros_data:
            Registros.objects.create(
                sitio=site,
                registro0=registros_data.get('registro0', False),
                registro1=registros_data.get('registro1', False),
                registro2=registros_data.get('registro2', False)
            )
        
        return site
    
    def update(self, instance, validated_data):
        registros_data = validated_data.pop('registros_data', {})
        
        # Actualizar sitio
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar o crear registros
        if registros_data:
            registro, created = Registros.objects.get_or_create(sitio=instance)
            for key, value in registros_data.items():
                if hasattr(registro, key):
                    setattr(registro, key, value)
            registro.save()
        
        return instance
    

