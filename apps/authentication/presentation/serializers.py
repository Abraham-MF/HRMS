from rest_framework import serializers
from ..infrastructure.models import User


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'email', 'username', 'role', 'is_active']
        read_only_fields = fields
