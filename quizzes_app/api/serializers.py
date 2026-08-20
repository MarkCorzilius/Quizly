from urllib.parse import parse_qs, urlparse

from rest_framework import serializers

from quizzes_app.models import Quiz, QuizQuestion


class QuizCreateSerializer(serializers.ModelSerializer):
    """Validates a YouTube URL and normalizes it before quiz creation."""

    url = serializers.URLField(required=True, source='video_url')

    class Meta:
        model = Quiz
        fields = ['url']

    def validate_video_url(self, value):
        """Reject non-YouTube URLs and normalize valid ones to a canonical watch URL."""

        video_id = self.extract_youtube_id(value)
        if not video_id:
            raise serializers.ValidationError(
                "Only valid YouTube URLs are allowed."
            )
        return f"https://www.youtube.com/watch?v={video_id}"

    def extract_youtube_id(self, value):
        """Extract the video id from a youtu.be or youtube.com URL, or return None."""

        parsed = urlparse(value)
        if parsed.hostname in ["youtu.be"]:
            return parsed.path.strip("/")
        if parsed.hostname in ["youtube.com", "www.youtube.com"]:
            return parse_qs(parsed.query).get("v", [None])[0]
        return None


class QuizQuestionSerializer(serializers.ModelSerializer):
    """Serializes a quiz question and validates that the answer is among its options."""

    class Meta:
        model = QuizQuestion
        fields = [
            'id',
            'question_title',
            'question_options',
            'answer',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):
        """Ensure the answer is one of the provided question options."""

        options = attrs.get('question_options')
        answer = attrs.get('answer')

        if answer not in options:
            raise serializers.ValidationError({'answer': 'Answer must be one of the question options.'})
        return attrs


class QuizSerializer(serializers.ModelSerializer):
    """Serializes a quiz together with its nested questions."""

    questions = QuizQuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = [
            'id',
            'title',
            'description',
            'created_at',
            'updated_at',
            'video_url',
            'questions',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]