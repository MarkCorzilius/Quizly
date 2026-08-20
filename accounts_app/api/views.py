from django.conf import settings

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from django.contrib.auth.models import User

from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView
from rest_framework_simplejwt.views import TokenObtainPairView


from accounts_app.api.serializers import RegisterSerializer
from accounts_app.api.authentication import CookieJWTAuthentication

from rest_framework.response import Response

COOKIE_KWARGS = {
    "httponly": True,
    "secure": not settings.DEBUG,
    "samesite": "Lax",
}


class RegisterView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({
            "detail": "User created successfully!"
        },
        status=status.HTTP_201_CREATED
        )

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            user = User.objects.get(username=request.data['username'])
            access = response.data["access"]
            refresh = response.data["refresh"]

            final_response = Response({
                "detail": "Login successfully!",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    },
                    "access": access,
                    "refresh": refresh,
                    },
                    status=status.HTTP_200_OK
                    )
            final_response.set_cookie("access_token", access, **COOKIE_KWARGS)
            final_response.set_cookie("refresh_token", refresh, **COOKIE_KWARGS)
            return final_response
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        request.data["refresh"] = request.data.get("refresh") or request.COOKIES.get("refresh_token")

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            response.set_cookie("access_token", response.data["access"], **COOKIE_KWARGS)
            if response.data.get("refresh"):
                response.set_cookie("refresh_token", response.data["refresh"], **COOKIE_KWARGS)
        return response


class LogoutView(TokenBlacklistView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.data["refresh"] = request.data.get("refresh") or request.COOKIES.get("refresh_token")

        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            final_response = Response({
                "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
                })
            final_response.delete_cookie("access_token")
            final_response.delete_cookie("refresh_token")
            return final_response
        return response