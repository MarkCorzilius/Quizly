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


class BaseModelTestCase(APITestCase):
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

class QuizModelTests(BaseModelTestCase):
    """Tests for the Quiz model."""

    def setUp(self):
        """Run the base setup."""

        super().setUp()

    @patch("quizzes_app.api.views.create_quiz", return_value=MOCK_QUIZ_DATA)
    def test_create_quiz(self, mock_create):
        """Creating a quiz via the API persists it in the database."""

        response = self.client.post(
            "/api/quizzes/",
            {
                "url": "https://www.youtube.com/watch?v=WH_ieAsb4AI"
            },
            format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Quiz.objects.filter(id=response.data['id']).exists())
        self.assertEqual(Quiz.objects.count(), 1)

    def test_deleting_quiz_deletes_questions(self):
        """Deleting a quiz cascades and removes its questions."""

        quiz = Quiz.objects.create(
            creator=self.user,
            title="Python Quiz",
            description="Small Quiz to test python knowledge",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
        )
        quiz.delete()

        self.assertEqual(QuizQuestion.objects.count(), 0)

    def test_timestamps_are_created(self):
        """A created quiz has created_at and updated_at timestamps set."""

        quiz = Quiz.objects.create(
            creator=self.user,
            title="Python Quiz",
            description="Small Quiz to test python knowledge",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
        )

        self.assertIsNotNone(quiz.created_at)
        self.assertIsNotNone(quiz.updated_at)


class QuizQuestionModelTests(BaseModelTestCase):
    """Tests for the QuizQuestion model."""

    def setUp(self):
        """Create a base quiz with one question."""

        super().setUp()
        
        self.quiz = Quiz.objects.create(
            creator=self.user,
            title="Python Quiz",
            description="Small Quiz to test python knowledge",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
        )

        self.question = QuizQuestion.objects.create(
            quiz=self.quiz,
            question_title="What is Python?",
            question_options=["Company", "Film", "Programming Language"],
            answer="Programming Language",
        )

    @patch("quizzes_app.api.views.create_quiz", return_value=MOCK_QUIZ_DATA)
    def test_create_quiz_questions(self, mock_create):
        """Creating a quiz via the API persists its questions in the database."""

        response = self.client.post(
            "/api/quizzes/",
            {
                "url": "https://www.youtube.com/watch?v=WH_ieAsb4AI"
            },
            format="json"
            )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(QuizQuestion.objects.filter(id=self.question.id).exists())
        self.assertTrue(QuizQuestion.objects.count(), 1)
        self.assertEqual(self.question.quiz, self.quiz)
        self.assertEqual(QuizQuestion.objects.first(), self.question)

    def test_timestamps_are_created(self):
        """A created question's quiz has created_at and updated_at timestamps set."""

        self.assertIsNotNone(self.quiz.created_at)
        self.assertIsNotNone(self.quiz.updated_at)

