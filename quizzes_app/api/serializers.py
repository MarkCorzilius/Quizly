from rest_framework import serializers
from quizzes_app.api.serializers import QuizSerializer, QuizQuestionSerializer
class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSerializer
        fields = [
            'id',
            'title',
            'description',
            'created_at',
            'updated_at',
            'video_url',
            'questions',
        ]

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestionSerializer
        fields = [
            'id',
            'question_title',
            'question_options',
            'answer',
            'created_at',
            'updated_at',
        ]

