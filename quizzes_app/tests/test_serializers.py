from rest_framework.test import APITestCase
from quizzes_app.models import Quiz, QuizQuestion
from quizzes_app.api.serializers import QuizSerializer, QuizQuestionSerializer
from django.contrib.auth.models import User

class BaseSerializerTestCase(APITestCase):
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
        
        self.valid_quiz_data = {
            "creator": self.user,
            "title": "Python Quiz",
            "description": "Python basics",
            "video_url": "https://www.youtube.com/watch?v=WH_ieAsb4AI",
            }



class QuizSerializerTestCase(BaseSerializerTestCase):
    def setUp(self):
        super().setUp()
        self.expected_fields = {
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions"
            }

    def test_required_fields(self):
        required_fields = [
            'title',
            'description',
            'video_url',
            ]

        for field in required_fields:
            data = self.valid_quiz_data.copy()
            data.pop(field)
            serializer = QuizSerializer(data=data)

            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)

    def test_invalid_title(self):
        data = self.valid_quiz_data.copy()
        data['title'] = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        serializer = QuizSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_invalid_description(self):
        data = self.valid_quiz_data.copy()
        data['description'] = 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
        serializer = QuizSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('description', serializer.errors)

    def test_invalid_video_url(self):
        invalid_urls = [
            'not-a-url',
            '123',
            'hello',
        ]
        for url in invalid_urls:
            data = self.valid_quiz_data.copy()
            data['video_url'] = url
            serializer = QuizSerializer(data=data)

            self.assertFalse(serializer.is_valid())
            self.assertIn('video_url', serializer.errors)

    def test_serialized_output(self):
        quiz = Quiz.objects.create(
            creator=self.user,
            title="Python Quiz",
            description="Python basics",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
            )
        serializer = QuizSerializer(quiz)
        print("abc1: ", set(serializer.data.keys()))
        print("abc2: ", self.expected_fields)
        self.assertEqual(set(serializer.data.keys()), self.expected_fields)
        
    def test_nested_question_relationship(self):
        quiz = Quiz.objects.create(
            creator=self.user,
            title="Python Quiz",
            description="Python basics",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
            )
        question = QuizQuestion.objects.create(
            quiz=quiz,
            question_title="What is Python?",
            question_options=["Option A", "Option B"],
            answer="Option A",
            )
        serializer = QuizSerializer(quiz)

        self.assertEqual(len(serializer.data['questions']), 1)
        self.assertEqual(serializer.data['questions'][0]['id'], question.id)


class QuizQuestionSerializerTestCase(BaseSerializerTestCase):
    def setUp(self):
        super().setUp()
        self.valid_question_data = {
            "question_title": "What is Python?",
            "question_options": ["Option A", "Option B", "Option C"],
            "answer": "Option A",
            }

        self.quiz = Quiz.objects.create(**self.valid_quiz_data)
        self.expected_fields = {
            "id",
            "question_title",
            "question_options",
            "answer",
            "created_at",
            "updated_at",
            }

    def test_required_fields(self):
        required_fields = [
            'question_title',
            'question_options',
            'answer',
            ]

        for field in required_fields:
            data = {
            'question_title': 'Do you like Python?',
            'question_options': ['Option A', 'Option B', 'Option C'],
            'answer': 'Option A',
            }

            data.pop(field)
            serializer = QuizQuestionSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)

    def test_invalid_question_title(self):
        data = self.valid_question_data.copy()
        data['question_title'] = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        serializer = QuizQuestionSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('question_title', serializer.errors)

    def test_invalid_question_options(self):
        data = self.valid_question_data.copy()
        data['question_options'] = ['Option A', 'Option B']
        data['answer'] = 'Option C'

        serializer = QuizQuestionSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('answer', serializer.errors)


    def test_invalid_question_answer(self):
        data = self.valid_question_data.copy()
        invalid_answers = {
            '',
            'Option Not Existing',
            }
        for invalid_answer in invalid_answers:
            data['answer'] = invalid_answer
            serializer = QuizQuestionSerializer(data=data)

            self.assertFalse(serializer.is_valid())
            self.assertIn('answer', serializer.errors)

    def test_serialized_output(self):
        quiz = Quiz.objects.create(
            creator=self.user,
            title="Python Quiz",
            description="Python basics",
            video_url="https://www.youtube.com/watch?v=WH_ieAsb4AI",
            )

        quiz_question = QuizQuestion.objects.create(
            quiz=quiz,
            question_title="What is Python?",
            question_options=["Option A", "Option B"],
            answer="Option A",
            )
        serializer = QuizQuestionSerializer(quiz_question)
 
        self.assertEqual(set(serializer.data.keys()), self.expected_fields)

