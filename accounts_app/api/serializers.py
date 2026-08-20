from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    """Validates registration data and creates a new user with a matching password pair."""

    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password']

    def validate(self, attrs):
        """Ensure password and repeated_password match, then drop repeated_password."""

        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})

        attrs.pop('repeated_password')

        return attrs

    def create(self, validated_data):
        """Create the user with a properly hashed password."""

        return User.objects.create_user(**validated_data)