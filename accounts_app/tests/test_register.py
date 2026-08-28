from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.core.cache import cache


class RegisterTestCase(APITestCase):
    """Tests for the register endpoint."""

    def setUp(self):
        """Create an existing user used to test duplicate registration."""
        
        cache.clear()
        self.first_user = User.objects.create_user(
            username="firstuser",
            email="firstuser@gmail.com",
            password="password123"
            )

    def test_register_success(self):
        """Registering with valid data creates the user."""

        response = self.client.post(
            "/api/register/",
            {
                "username": "testuser",
                "email": "testuser@gmail.com",
                "password": "password123",
                "confirmed_password": "password123",
                },
                format="json"
                )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_unsafe_password(self):
        """Registering with mismatched passwords is rejected and no user is created."""

        response = self.client.post(
            "/api/register/",
            {
                "username": "testuser",
                "email": "testuser@gmail.com",
                "password": "huhu",
                "confirmed_password": "password123",
                },
                format="json"
                )
        
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_register_existing_user(self):
        """Registering with an already taken username is rejected."""

        response = self.client.post(
            "/api/register/",
            {
                "username": "firstuser",
                "email": "firstuser@gmail.com",
                "password": "password123",
                "confirmed_password": "password123",
                },
                format="json"
                )
        
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_register_throttle(self):
        last_user_data = {
                "username": f"lastuser@example.com",
                "password": "Password123!",
                "confirmed_password": "Password123!",
            }
        for i in range(10):
            data = {
                "username": f"user{i}@example.com",
                "password": "Password123!",
                "confirmed_password": "Password123!",
            }
            response = self.client.post("/api/register/", data, format="json", REMOTE_ADDR="192.168.1.1")
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        response = self.client.post("/api/register/", last_user_data, format="json", REMOTE_ADDR="192.168.1.1")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_different_ips_have_different_throttle_rates(self):
        last_user_data = {
                "username": f"lastuser@example.com",
                "password": "Password123!",
                "confirmed_password": "Password123!",
            }
        for i in range(10):
            data = {
                "username": f"user{i}@example.com",
                "password": "Password123!",
                "confirmed_password": "Password123!",
            }
            response = self.client.post("/api/register/", data, format="json", REMOTE_ADDR="192.168.1.1")
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        response = self.client.post("/api/register/", data, format="json", REMOTE_ADDR="192.168.1.1")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        response = self.client.post("/api/register/", last_user_data, format="json", REMOTE_ADDR="192.168.1.2")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
