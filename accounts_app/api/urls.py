from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from accounts_app.api.views import LogoutView, RegisterView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='token_blacklist'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]