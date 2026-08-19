from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from quizzes_app.models import Quiz, QuizQuestion
from django.contrib.auth.models import User

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
        self.quiz = Quiz.objects.create(
            title="Python Quiz",
            description="Small Quiz to test python knowledge",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
        )

    def test_create_quiz(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Quiz.objects.filter(id=self.quiz.id).exists())
        self.assertEqual(Quiz.objects.count(), 1)

    def test_deleting_quiz_deletes_questions(self):
        self.quiz.delete()
        self.assertEqual(QuizQuestion.objects.count(), 0)

    def test_timestamps_are_created(self):
        self.assertIsNotNone(self.quiz.created_at)
        self.assertIsNotNone(self.quiz.updated_at)

        

class QuizQuestionModelTests(BaseModelTestCase):
    def setUp(self):
        super().setUp()
        
        self.quiz = Quiz.objects.create(
            title="Python Quiz",
            description="Small Quiz to test python knowledge",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
        )

        self.question = QuizQuestion.objects.create(
            quiz=self.quiz,
            title="What is Python?",
            question_options=["Company", "Film", "Programming Language"],
            answer="Programming Language",
        )

    def test_create_quiz_questions(self):

        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(QuizQuestion.objects.filter(id=self.question.id).exists())
        self.assertTrue(QuizQuestion.objects.count(), 1)
        self.assertEqual(self.question.quiz, self.quiz)
        self.assertEqual(QuizQuestion.objects.first(), self.question)

    def test_timestamps_are_created(self):
        self.assertIsNotNone(self.quiz.created_at)
        self.assertIsNotNone(self.quiz.updated_at)

