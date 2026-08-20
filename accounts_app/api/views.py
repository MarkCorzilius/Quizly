from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from accounts_app.api.authentication import CookieJWTAuthentication
from accounts_app.api.serializers import RegisterSerializer

COOKIE_KWARGS = {
    "httponly": True,
    "secure": not settings.DEBUG,
    "samesite": "Lax",
}


class RegisterView(CreateAPIView):
    """Creates a new user account from valid registration data."""

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        """Create the user and return a simple success message."""

        super().create(request, *args, **kwargs)
        return Response({
            "detail": "User created successfully!"
        },
        status=status.HTTP_201_CREATED
        )


class LoginView(TokenObtainPairView):
    """Authenticates a user and returns/sets JWT access and refresh tokens."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Issue tokens on successful login and store them as httponly cookies."""

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
    """Refreshes the access token using the refresh_token cookie."""

    def post(self, request, *args, **kwargs):
        """Read the refresh token from the cookie and set the new tokens as cookies."""

        request.data["refresh"] = request.data.get("refresh") or request.COOKIES.get("refresh_token")

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            response.set_cookie("access_token", response.data["access"], **COOKIE_KWARGS)
            if response.data.get("refresh"):
                response.set_cookie("refresh_token", response.data["refresh"], **COOKIE_KWARGS)
        return response


class LogoutView(TokenBlacklistView):
    """Blacklists the refresh token and clears the auth cookies."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Blacklist the refresh token and delete the auth cookies on success."""

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
