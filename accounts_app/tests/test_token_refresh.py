from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class RegisterTestCase(APITestCase):
    def setUp(self):
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

    def test_token_success(self):
        response = self.client.post(
            "/api/token/refresh/",
            {
                "refresh": self.refresh_token
            },
            format="json"
            )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_invalid_refresh_token(self):
        response = self.client.post(
            "/api/token/refresh/",
            {
                "refresh": "invalid-token"
            },
            format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_refresh_token(self):
        first_response = self.client.post(
            "/api/logout/",
            {"refresh": self.refresh_token},
            format="json"
            )
        print("asd", first_response.data)
        
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        sec_response = self.client.post(
            "/api/token/refresh/",
            {"refresh": self.refresh_token},
            format="json"
            )
        self.assertEqual(sec_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
           

    