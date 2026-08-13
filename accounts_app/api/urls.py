from django.urls import path
from accounts_app.api.views import LogoutView, RegisterView, LoginView, RefreshTokenView


urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='token_blacklist'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
]