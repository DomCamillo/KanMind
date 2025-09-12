
from tasks.models import Comment, Task
from boards.models import Column ,Board, BoardUser,STATUS_CHOICES
from authentication.api.permissions import IsActiveUser
from .serializers import   RegistrationSerializer
from django.contrib.auth import authenticate, get_user_model

from django.http import Http404
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAuthenticated ,NotFound, PermissionDenied ,ValidationError
from rest_framework import serializers


"""-------LOGIN/REGISTRATION VIEW---------"""

class LoginView(APIView):
    """ Custom login endpoint.
    Authenticates user by email + password, returns token and user info."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=400)

        auth_user = authenticate(username=user.username, password=password)
        if auth_user is not None:
            token, created = Token.objects.get_or_create(user=auth_user)
            return Response({
                "token": token.key,
                "fullname": auth_user.username,
                "email": auth_user.email,
                "user_id": auth_user.id,
            }, status=200)
        return Response({"error": "Invalid email or password"}, status=400)


class RegistrationView(APIView):
    """ Handles user registration.
     On success, returns token and created user info."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "fullname": user.username,
                "email": user.email,
                "user_id": user.id,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




"""-------EMAIL-CHECK VIEW---------"""

User = get_user_model()
class EmailCheckView(APIView):
    """ Checks whether an email is already registered.
     Supports both GET (query param) and POST (body)."""
    permission_classes = [AllowAny]

    def _find_user_by_email(self, email):
        email = (email or '').strip()
        if not email:
            return None
        return User.objects.filter(email__iexact=email).first()

    def get(self, request):
        email = request.query_params.get('email', '')
        user = self._find_user_by_email(email)
        if user:
            return Response({
                "email_exists": True,
                "id": user.id,
                "email": user.email,
                "fullname": user.username
            })
        return Response({"email_exists": False})

    def post(self, request):
        email = request.data.get('email', '')
        user = self._find_user_by_email(email)
        if user:
            return Response({
                "email_exists": True,
                "id": user.id,
                "email": user.email,
                "fullname": user.username
            })
        return Response({"email_exists": False})

