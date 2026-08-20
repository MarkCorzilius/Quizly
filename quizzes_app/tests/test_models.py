from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from quizzes_app.models import Quiz, QuizQuestion
from django.contrib.auth.models import User
from unittest.mock import patch

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
    def setUp(self):
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
    def setUp(self):
        super().setUp()

    @patch("quizzes_app.api.views.create_quiz", return_value=MOCK_QUIZ_DATA)
    def test_create_quiz(self, mock_create):
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
        quiz = Quiz.objects.create(
            creator=self.user,
            title="Python Quiz",
            description="Small Quiz to test python knowledge",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
        )
        quiz.delete()

        self.assertEqual(QuizQuestion.objects.count(), 0)

    def test_timestamps_are_created(self):
        quiz = Quiz.objects.create(
            creator=self.user,
            title="Python Quiz",
            description="Small Quiz to test python knowledge",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
        )

        self.assertIsNotNone(quiz.created_at)
        self.assertIsNotNone(quiz.updated_at)

        

class QuizQuestionModelTests(BaseModelTestCase):
    def setUp(self):
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
        self.assertIsNotNone(self.quiz.created_at)
        self.assertIsNotNone(self.quiz.updated_at)

