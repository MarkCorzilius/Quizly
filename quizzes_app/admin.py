from django.contrib import admin
from quizzes_app.models import Quiz, QuizQuestion


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):

    search_fields = (
        "title",
        "description",
        "creator__username",
    )

    list_filter = (
        "created_at",
        "creator",
    )

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):

    search_fields = (
        "title",
        "quiz__title",
    )

    list_filter = (
        "quiz",
    )