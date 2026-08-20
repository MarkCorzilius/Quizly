from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Reads the access token from the Authorization header first,
    falls back to the httponly 'access_token' cookie (used by the frontend)."""

    def authenticate(self, request):
        """Authenticate via the Authorization header, or fall back to the access_token cookie."""

        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
