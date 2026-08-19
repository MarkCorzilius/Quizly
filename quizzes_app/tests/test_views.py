from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from quizzes_app.models import Quiz, QuizQuestion
from quizzes_app.api.serializers import QuizSerializer, QuizQuestionSerializer
from django.contrib.auth.models import User

class BaseQuizViewTestCase(APITestCase):
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

class QuizViewTests(BaseQuizViewTestCase):

    def setUp(self):
        super().setUp()

    def test_unathenticated_request(self):
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

    def test_create_quiz(self):
        response = self.client.post(
            "/api/quizzes/",
            {
                "url":"https://www.youtube.com/watch?v=WH_ieAsb4AI"
            },
            format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_quiz_invalid_data(self):
        response = self.client.post(
            "/api/quizzes/",
            {
                "username":"testuser"
            },
            format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
       
    def test_list_quizzes(self):
        self.client.post(
            "/api/quizzes/",
            {
                "url":"https://www.youtube.com/watch?v=WH_ieAsb4AI"
            },
            format="json"
            )
        response = self.client.get("/api/quizzes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(QuizQuestion.objects.count(), 1)
        self.assertEqual(len(response.data), 1)

    def test_empty_list_quizzes(self):
        response = self.client.get("/api/quizzes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_retrieve_quiz(self):
        self.client.post(
            "/api/quizzes/",
            {
                "url":"https://www.youtube.com/watch?v=WH_ieAsb4AI"
            },
            format="json"
            )

        response = self.client.get("/api/quizzes/1/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)

    def test_retrieve_quiz_not_found(self):
        self.client.post(
            "/api/quizzes/",
            {
                "url":"https://www.youtube.com/watch?v=WH_ieAsb4AI"
            },
            format="json"
            )

        response = self.client.get("/api/quizzes/9999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_foreign_quiz_not_allowed(self):
        quiz_response = self.client.post(
            "/api/quizzes/",
            {
                "url":"https://www.youtube.com/watch?v=WH_ieAsb4AI"
            },
            format="json"
            )
        quiz_id = quiz_response.data["id"]

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
        
        response = self.client.get(f"/api/quizzes/{quiz_id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_update_quiz(self):
        quiz_response = self.client.post(
            "/api/quizzes/",
            {
                "url":"https://www.youtube.com/watch?v=WH_ieAsb4AI"
            },
            format="json"
            )
        quiz_id = quiz_response.data["id"]

        response = self.client.patch(
            f"/api/quizzes/{quiz_id}/",
            {
                "title": "Partially Updated Title",
                "description": "Partially Updated Description"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_quiz_keeps_unspecified_fields(self):
        quiz = Quiz.objects.create(
            creator=self.user,
            title="Old title",
            description="Old Description",
            url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
            )

        response = self.client.patch(
            f"/api/quizzes/{quiz.creator}/",
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
        Quiz.objects.create(
            creator=self.user,
            title="Old title",
            description="Old Description",
            url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
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
        quiz_response = Quiz.objects.create(
            creator=self.user,
            title="Old title",
            description="Old Description",
            url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
            )

        quiz_id = quiz_response.data['id']

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
            f"/api/quizzes/{quiz_id}/",
            {
                "title": "New Title",
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_delete_quiz(self):
        quiz = Quiz.objects.create(
            creator=self.user,
            title="Old title",
            description="Old Description",
            url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
            )
        response = self.client.delete(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(QuizQuestion.objects.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        

    def test_delete_quiz_not_found(self):
        response = self.client.delete("/api/quizzes/9999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)