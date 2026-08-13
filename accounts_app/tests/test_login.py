from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User

class LoginTestCase(APITestCase):
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
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
            )

    def test_login_success(self):
        self.assertEqual(status.HTTP_200_OK, self.response.status_code)
        self.assertIn("access", self.response.data)
        self.assertIn("refresh", self.response.data)
        
    def test_login_wrong_password(self):
        response = self.client.post(
            "/api/login/",
            {
                "username": "testuser",
                "password": "wrongPassword123"
                },
                format="json"
                )
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_login_into_unexisting_account(self):
        response = self.client.post(
            "/api/login/",
            {
                "username": "not_existing_user",
                "password": "password123"
                },
                format="json"
                )

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)