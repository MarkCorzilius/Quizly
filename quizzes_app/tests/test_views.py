from unittest.mock import patch

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from quizzes_app.models import Quiz, QuizQuestion


MOCK_QUIZ_DATA = {
            "id": 1,
            "title": "Mock Quiz",
            "description": "Mock Description",
            "questions": [
                {
                    "question_title": "What is this about?",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "A"
                    }
                    ]
                    }

class BaseQuizViewTestCase(APITestCase):
    """Base test case that logs in a test user before each test."""

    def setUp(self):
        """Create a test user and log in to obtain an access token."""

        self.user = User.objects.create_user(
            username="testuser",
            password="password123"
            )

        self.client = APIClient()
        
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
        

class QuizViewTests(BaseQuizViewTestCase):

    def setUp(self):
        """Run the base setup."""

        super().setUp()

    def test_unathenticated_request(self):
        """An unauthenticated request to create a quiz is rejected."""

        self.client.credentials()
        response = self.client.post(
            "/api/quizzes/",
            {
                "url":"https://www.youtube.com/watch?v=WH_ieAsb4AI"
            },
            format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(QuizQuestion.objects.count(), 0)

    @patch("quizzes_app.api.views.create_quiz", return_value=MOCK_QUIZ_DATA)
    def test_create_quiz(self, mock_create):
        """Creating a quiz with a valid URL returns a 201 response."""

        response = self.client.post(
            "/api/quizzes/",
            {"url": "https://www.youtube.com/watch?v=WH_ieAsb4AI"},
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_quiz_invalid_data(self):
        """Creating a quiz without a valid URL is rejected."""

        response = self.client.post(
            "/api/quizzes/",
            {
                "username":"testuser"
            },
            format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_quizzes(self):
        """Listing quizzes returns all quizzes owned by the user."""

        quiz = Quiz.objects.create(
            creator=self.user,
            title="Test Quiz",
            description="Test Description",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
            )

        QuizQuestion.objects.create(
            quiz=quiz,
            question_title="Test question",
            question_options=['A', 'B', 'C', 'D'],
            answer="A",
        )

        response = self.client.get("/api/quizzes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(QuizQuestion.objects.count(), 1)
        self.assertEqual(len(response.data), 1)

    def test_empty_list_quizzes(self):
        """Listing quizzes returns an empty result when none exist."""

        response = self.client.get("/api/quizzes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_retrieve_quiz(self):
        """Retrieving an owned quiz returns its details."""

        quiz = Quiz.objects.create(
            creator=self.user,
            title="Test Quiz",
            description="Test Description",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
            )

        QuizQuestion.objects.create(
            quiz=quiz,
            question_title="Test question",
            question_options=['A', 'B', 'C', 'D'],
            answer="A",
        )

        response = self.client.get(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)

    def test_retrieve_quiz_not_found(self):
        """Retrieving a non-existing quiz returns a 404 response."""

        response = self.client.get("/api/quizzes/9999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_foreign_quiz_not_allowed(self):
        """Retrieving another user's quiz returns a 404 response."""

        quiz = Quiz.objects.create(
            creator=self.user,
            title="Test Quiz",
            description="Test Description",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
            )

        QuizQuestion.objects.create(
            quiz=quiz,
            question_title="Test question",
            question_options=['A', 'B', 'C', 'D'],
            answer="A",
        )

        User.objects.create_user(username="ForeignUser", password="password123")

        response = self.client.post(
            "/api/login/",
            {
                "username": "ForeignUser",
                "password": "password123"
                },
                format="json"
                )
        access_token = response.data['access']
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
            )
        
        response = self.client.get(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_quiz(self):
        """Partially updating an owned quiz succeeds."""

        quiz = Quiz.objects.create(
            creator=self.user,
            title="Test Quiz",
            description="Test Description",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
            )

        QuizQuestion.objects.create(
            quiz=quiz,
            question_title="Test question",
            question_options=['A', 'B', 'C', 'D'],
            answer="A",
        )

        response = self.client.patch(
            f"/api/quizzes/{quiz.id}/",
            {
                "title": "Partially Updated Title",
                "description": "Partially Updated Description"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_quiz_keeps_unspecified_fields(self):
        """Updating only some fields keeps the other fields unchanged."""

        quiz = Quiz.objects.create(
            creator=self.user,
            title="Old Title",
            description="Old Description",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
            )

        response = self.client.patch(
            f"/api/quizzes/{quiz.id}/",
            {
                "title": "New Title",
            },
            format="json"
        )
        quiz.refresh_from_db()
        
        self.assertEqual(quiz.title, "New Title")
        self.assertEqual(quiz.description, "Old Description")
        self.assertEqual(quiz.creator, self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_quiz_not_found(self):
        """Updating a non-existing quiz returns a 404 response."""

        Quiz.objects.create(
            creator=self.user,
            title="Old title",
            description="Old Description",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
            )

        response = self.client.patch(
            "/api/quizzes/9999/",
            {
                "title": "New Title",
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_quiz_foreign_user_not_allowed(self):
        """Updating another user's quiz returns a 404 response."""

        quiz = Quiz.objects.create(
            creator=self.user,
            title="Old title",
            description="Old Description",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
            )

        User.objects.create_user(username="ForeignUser", password="password123")
        response = self.client.post(
            "/api/login/",
            {
                "username": "ForeignUser",
                "password": "password123"
                },
                format="json"
                )

        access_token = response.data['access']
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
            )

        response = self.client.patch(
            f"/api/quizzes/{quiz.id}/",
            {
                "title": "New Title",
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_delete_quiz(self):
        """Deleting an owned quiz removes it and its questions."""

        quiz = Quiz.objects.create(
            creator=self.user,
            title="Old title",
            description="Old Description",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
            )
        response = self.client.delete(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(QuizQuestion.objects.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        

    def test_delete_quiz_not_found(self):
        """Deleting a non-existing quiz returns a 404 response."""

        response = self.client.delete("/api/quizzes/9999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)