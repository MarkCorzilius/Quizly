from rest_framework import serializers

from django.contrib.auth.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})

        attrs.pop('repeated_password')

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)