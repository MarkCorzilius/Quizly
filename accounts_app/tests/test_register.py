from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User

class RegisterTestCase(APITestCase):
    def setUp(self):
        self.first_user = User.objects.create_user(
            username="firstuser",
            email="firstuser@gmail.com",
            password="password123"
            )

    def test_register_success(self):
        response = self.client.post(
            "/api/register/",
            {
                "username": "testuser",
                "email": "testuser@gmail.com",
                "password": "password123",
                "repeated_password": "password123",
                },
                format="json"
                )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_unsafe_password(self):
        response = self.client.post(
            "/api/register/",
            {
                "username": "testuser",
                "email": "testuser@gmail.com",
                "password": "huhu",
                "repeated_password": "password123",
                },
                format="json"
                )
        
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_register_existing_user(self):
        response = self.client.post(
            "/api/register/",
            {
                "username": "firstuser",
                "email": "firstuser@gmail.com",
                "password": "password123",
                "repeated_password": "password123",
                },
                format="json"
                )
        
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
