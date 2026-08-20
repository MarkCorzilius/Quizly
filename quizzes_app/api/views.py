from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from quizzes_app.api.serializers import QuizSerializer, QuizCreateSerializer
from quizzes_app.models import Quiz, QuizQuestion
from rest_framework import status
from rest_framework.response import Response
from quizzes_app.services.quiz_creator import create_quiz


class QuizViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return QuizCreateSerializer
        return QuizSerializer

    def get_queryset(self):
        return Quiz.objects.filter(creator=self.request.user)

    def get_object(self):
        obj = super().get_object()
        if obj.creator != self.request.user:
            self.permission_denied(self.request)
        return obj

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video_url = serializer.validated_data["video_url"]

        quiz_data = create_quiz(video_url)

        quiz = Quiz.objects.create(
            creator=self.request.user,
            title=quiz_data.get("title", "Untitled"),
            description=quiz_data.get("description", ""),
            video_url=video_url
            )
        
        for q in quiz_data.get("questions", []):
            QuizQuestion.objects.create(
                quiz=quiz,
                question_title=q.get("question_title"),
                question_options=q.get("question_options"),
                answer=q.get("answer")
            )

        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)

