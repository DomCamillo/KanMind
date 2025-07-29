from rest_framework import generics
from Kan_Mind_app.models import Column, Task, Comment, Board, BoardUser
from .serializers import BoardSerializer ,BoardUserSerializer, ColumnSerializer, TasksSerializer, CommentSerializer, RegistrationSerializer
from rest_framework.generics import ListAPIView
from rest_framework import status, viewsets
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny ,IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from .permissions import isOwnerOrAdmin, isUserOrReadOnly ,IsAdminForCrud, isAdminOnly, isBoardUser ,isBaordAdmin, isCommentAuthorOrAdmin

class BoardUserView(generics.ListCreateAPIView):
    queryset = BoardUser.objects.all()
    serializer_class = BoardUserSerializer
    permission_classes = [isBoardUser or isBaordAdmin & IsAuthenticated]

class BoardUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoardUser.objects.all()
    serializer_class = BoardUserSerializer
    permission_classes = [isBoardUser or isBaordAdmin & IsAuthenticated]

class ColumnView(generics.ListCreateAPIView):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [isUserOrReadOnly & isBoardUser]

class ColumnDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [isBoardUser or isBaordAdmin]

    def get_queryset(self):
        return Column.objects.filter(board__boarduser__user=self.request.user)


class CommentView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [isCommentAuthorOrAdmin]

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [isCommentAuthorOrAdmin]





class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Überprüfen, ob ein User mit dieser E-Mail existiert
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=400)

        # Authentifizieren mit Benutzername (nicht E-Mail!) und Passwort
        auth_user = authenticate(username=user.username, password=password)

        if auth_user is not None:
            token, created = Token.objects.get_or_create(user=auth_user)
            return Response({
                "token": token.key,
                "username": auth_user.username,
                "email": auth_user.email,
            })
        else:
            return Response({"error": "Invalid email or password"}, status=400)







# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         email = request.data.get("email")
#         password = request.data.get("password")
#         data = {}

#         try:
#             user = User.objects.get(email=email)
#             auth_user = authenticate(username=user.username, password=password)
#             if auth_user:
#                 token, created = Token.objects.get_or_create(user=auth_user)
#                 data = {
#                     "token": token.key,
#                     "username": auth_user.username,
#                     "email": auth_user.email,}
#             else:
#                 data = {"error": "Invalid password"}
#         except User.DoesNotExist:
#             data = {"error": "User with this email does not exist"}

#         return Response(data)


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            saved_accoun = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_accoun)
            data = {
                'token':token.key,
                'username' : saved_accoun.username,
                'email': saved_accoun.email,
            }
        else:
            data=serializer.errors
        return Response(data)


class EmailCheckView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        exists = User.objects.filter(email=email).exists()
        return Response({'email_exists': exists})

class TasksReviewerView(generics.ListAPIView):
    serializer_class = TasksSerializer
    permission_classes = [isUserOrReadOnly]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
     queryset = Task.objects.all()
     serializer_class = TasksSerializer
     permission_classes = [isBoardUser & IsAuthenticated]

     def get_queryset(self):
      user = self.request.user
      if user.is_authenticated:
        return Task.objects.filter(column__board__members__user=user)
      return Task.objects.none()


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated or isBaordAdmin]#[isUserOrReadOnly or isBaordAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            raise NotAuthenticated("Du bist nicht eingeloggt.")
        return Board.objects.filter(members__user=user)

class TasksAssignedToMeView(ListAPIView):
    serializer_class = TasksSerializer
    permission_classes = [isUserOrReadOnly]

    def get_queryset(self):
       return Task.objects.filter(assigned_to=self.request.user)


