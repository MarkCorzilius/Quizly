from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.core.cache import cache


class LoginTestCase(APITestCase):
    """Tests for the login endpoint."""

    def setUp(self):
        """Create a test user and log in to obtain tokens."""
        
        cache.clear()
        self.username = "testuser"
        self.password = "Password123!"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )
        self.client = APIClient()

        self.correct_data = {
            "email": self.username,
            "password": self.password
        }
        
        self.response = self.client.post(
            "/api/login/",
            {
                "username": self.username,
                "password": self.password,
                },
                format="json"
                )
        self.access_token = self.response.data["access"]
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
            )

    def test_login_success(self):
        """Login with valid credentials returns access and refresh tokens."""

        self.assertEqual(status.HTTP_200_OK, self.response.status_code)
        self.assertIn("access", self.response.data)
        self.assertIn("refresh", self.response.data)

    def test_login_wrong_password(self):
        """Login with a wrong password is rejected as unauthorized."""

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
        """Login with a non-existing username is rejected as unauthorized."""

        response = self.client.post(
            "/api/login/",
            {
                "username": "not_existing_user",
                "password": "password123"
                },
                format="json"
                )

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_login_throttle(self):
        for _ in range(10):
            response = self.client.post("/api/login/", self.correct_data, format="json")
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        response = self.client.post("/api/login/", self.correct_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_different_emails_have_different_throttle_rates(self):
        for _ in range(10):
            response = self.client.post("/api/login/", self.correct_data, format="json")
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        response = self.client.post("/api/login/", self.correct_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        User.objects.create_user(username="foreignuser", password="securePassword123!", is_active=True)
        response = self.client.post("/api/login/", data={
            "username": "foreignuser",
            "password": "securePassword123!",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
