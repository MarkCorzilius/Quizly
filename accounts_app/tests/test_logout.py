from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class LogoutTestCase(APITestCase):
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
    

    def test_logout_success(self):
        self.assertEqual(status.HTTP_200_OK, self.response.status_code)