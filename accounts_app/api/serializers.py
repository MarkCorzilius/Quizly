from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    """Validates registration data and creates a new user with a matching password pair."""

    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirmed_password']

    def validate(self, attrs):
        """Ensure password and repeated_password match, then drop confirmed_password."""

        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})

        attrs.pop('confirmed_password')

        return attrs

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def create(self, validated_data):
        """Create the user with a properly hashed password."""

        return User.objects.create_user(**validated_data)