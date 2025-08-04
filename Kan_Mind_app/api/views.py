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
                "user" : {
                    "id": auth_user.id,
                    "username": auth_user.username,
                    "fullname": auth_user.username,
                    "email": auth_user.email,
                }

            })
        else:
            return Response({"error": "Invalid email or password"}, status=400)





class RegistrationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        print("REGISTRATION REQUEST:", request.data)
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "fullname": user.username,
                    "email": user.email,
                    }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get('email')
        exists = User.objects.filter(email=email).exists()
        return Response({'email_exists': exists})

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
            raise NotAuthenticated("You are not logged in")
        return Board.objects.filter(members__user=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TasksAssignedToMeView(ListAPIView):
    serializer_class = TasksSerializer
    permission_classes = [isUserOrReadOnly]

    def get_queryset(self):
       return Task.objects.filter(assigned_to=self.request.user)


