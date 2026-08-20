from rest_framework import routers
from quizzes_app.api.views import QuizViewSet

router = routers.SimpleRouter()
router.register(r'quizzes', QuizViewSet, basename='quiz')

urlpatterns = router.urls