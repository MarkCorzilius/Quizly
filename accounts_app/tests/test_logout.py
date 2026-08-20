from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class LogoutTestCase(APITestCase):
    """Tests for the logout endpoint."""

    def setUp(self):
        """Create a test user and log in to obtain tokens."""

        self.user = User.objects.create_user(
            username="testuser",
            password="password123"
            )
        
        self.response = self.client.post(
            "/api/login/",
            {
                "username": "testuser",
                "password": "password123"
                },
                format="json"
                )
        self.access_token = self.response.data["access"]
        self.refresh_token = self.response.data["refresh"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
            )

    def test_logout_success(self):
        """Logging in successfully returns a 200 response."""

        self.assertEqual(status.HTTP_200_OK, self.response.status_code)

    def test_logout_blacklists_refresh_token(self):
        """Logging out blacklists the refresh token so it can no longer be used."""

        first_response = self.client.post(
            "/api/logout/",
            {"refresh": self.refresh_token},
            format="json"
            )

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        sec_response = self.client.post(
            "/api/token/refresh/",
            {"refresh": self.refresh_token},
            format="json"
            )
        self.assertEqual(sec_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
