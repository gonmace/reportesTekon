from rest_framework import serializers
from .models import Site

class SiteSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Site
        fields = '__all__'

    def get_user(self, obj):
        return obj.user.username if obj.user else None
